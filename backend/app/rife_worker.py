import os
import subprocess
import shutil
from pathlib import Path
from typing import Literal, Optional

from settings import settings
from utils.video import (
    extract_frames,
    ensure_dir,
    auto_encode_video,   # 🔥 自動判定付きglob対応
)

RIFE_PY = Path(settings.rife_repo) / "inference_video.py"


class RIFEWorker:
    """
    RIFE フレーム補間処理を担当するバックエンドワーカー
    """

    def __init__(self, storage: str = settings.storage):
        self.storage = Path(storage)
        ensure_dir(self.storage)

    # ============================================================
    # 🎞️ 動画全体の補間
    # ============================================================
    def interpolate_video(self,
                          input_video: Path,
                          out_video: Path,
                          exp: int = 2,
                          fps: Optional[int] = None,
                          scale: Literal[1, 2, 4] = 1):
        """
        Practical-RIFE の inference_video.py を使って動画全体を補間
        - exp: 2 → 2x中間, 3 → 4x, 4 → 8x
        - fps: 出力FPSを指定。Noneなら元動画のFPSを維持
        - scale: 内部処理のスケール（高速化用）
        """
        work_dir = self.storage / "tmp_frames"
        ensure_dir(work_dir)

        # 元動画 → フレーム抽出
        extract_frames(input_video, work_dir, fps or 30)

        # RIFE による補間実行
        cmd = [
            "python3", str(RIFE_PY),
            "--img", str(work_dir),
            "--output", str(work_dir / "output"),
            "--exp", str(exp),
        ]
        print("🚀 Running RIFE:", " ".join(cmd))
        subprocess.run(cmd, check=True)

        # 出力されたフレーム群を動画に変換（glob対応）
        auto_encode_video(work_dir / "output", out_video, fps=fps or 30)

        print(f"✅ RIFE interpolation complete → {out_video}")
        return out_video

    # ============================================================
    # 🖼️ 2枚の画像から動画を生成
    # ============================================================
    def interpolate_two_frames(self,
                               frame_a: Path,
                               frame_b: Path,
                               out_video: Path,
                               num_mid: int = 6,
                               fps: int = 30):
        """
        2枚の画像の間に中間フレームを生成し、動画化
        """
        work_dir = Path(out_video).with_suffix("").parent / (out_video.stem + "_frames")
        if work_dir.exists():
            shutil.rmtree(work_dir)
        ensure_dir(work_dir)

        # 入力画像を一時ディレクトリにコピー
        tmp_pair = work_dir / "pair"
        ensure_dir(tmp_pair)
        shutil.copy(frame_a, tmp_pair / "000000.png")
        shutil.copy(frame_b, tmp_pair / "000001.png")

        # expを計算（num_midに応じて動的に決定）
        exp = 1
        while (2 ** exp) - 1 < num_mid:
            exp += 1

        # RIFE実行
        cmd = [
            "python3", str(RIFE_PY),
            "--img", str(tmp_pair),
            "--output", str(work_dir / "output"),
            "--exp", str(exp),
        ]
        print("🚀 Running RIFE (pair):", " ".join(cmd))
        subprocess.run(cmd, check=True)

        # 出力画像群を動画化（glob対応）
        auto_encode_video(work_dir / "output", out_video, fps=fps)

        print(f"🎬 Video created → {out_video}")

        job.output_url = f"/data/{job.id}_seq_frames/output/"  # ← ここ！！
        print(f"✅ 中間フレーム出力URL: {job.output_url}")
        return out_video

