import os
import subprocess
import shutil
from pathlib import Path
from typing import Literal, Optional

from settings import settings
from utils.video import (
    extract_frames,
    ensure_dir,
    auto_encode_video,   # glob対応
)

RIFE_PY = Path(settings.rife_repo) / "inference_video.py"


class RIFEWorker:
    """RIFE フレーム補間処理ワーカー"""

    def __init__(self, storage: str = settings.storage):
        self.storage = Path(storage)
        ensure_dir(self.storage)

    # ============================================================
    # 🎞️ 動画全体補間
    # ============================================================
    def interpolate_video(self,
                          input_video: Path,
                          out_video: Path,
                          exp: int = 2,
                          fps: Optional[int] = None,
                          scale: Literal[1, 2, 4] = 1):
        work_dir = self.storage / "tmp_frames"
        ensure_dir(work_dir)

        extract_frames(input_video, work_dir, fps or 30)

        cmd = [
            "python3", str(RIFE_PY),
            "--img", str(work_dir),
            "--output", str(work_dir / "output"),
            "--exp", str(exp),
        ]
        print("🚀 Running RIFE:", " ".join(cmd))
        subprocess.run(cmd, check=True)

        auto_encode_video(work_dir / "output", out_video, fps=fps or 30)
        print(f"✅ RIFE interpolation complete → {out_video}")
        return out_video

    # ============================================================
    # 🖼️ 2枚の画像補間
    # ============================================================
    def interpolate_two_frames(self,
                               frame_a: Path,
                               frame_b: Path,
                               out_video: Path,
                               num_mid: int = 6,
                               fps: int = 30):
        work_dir = Path(out_video).with_suffix("").parent / (out_video.stem + "_frames")
        if work_dir.exists():
            shutil.rmtree(work_dir)
        ensure_dir(work_dir)

        tmp_pair = work_dir / "pair"
        ensure_dir(tmp_pair)
        shutil.copy(frame_a, tmp_pair / "000000.png")
        shutil.copy(frame_b, tmp_pair / "000001.png")

        exp = 1
        while (2 ** exp) - 1 < num_mid:
            exp += 1

        cmd = [
            "python3", str(RIFE_PY),
            "--img", str(tmp_pair),
            "--output", str(work_dir / "output"),
            "--exp", str(exp),
        ]
        print("🚀 Running RIFE (pair):", " ".join(cmd))
        subprocess.run(cmd, check=True)

        auto_encode_video(work_dir / "output", out_video, fps=fps)
        print(f"🎬 Video created → {out_video}")

        # ❌ job は main.py 側で管理されるので、ここでは触らない
        return out_video

