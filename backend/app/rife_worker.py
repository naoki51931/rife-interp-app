import os
import subprocess
import shutil
from pathlib import Path
from typing import Literal, Optional

from settings import settings
from utils.video import extract_frames, encode_video_from_frames, ensure_dir

RIFE_PY = Path(settings.rife_repo) / "inference_video.py"


class RIFEWorker:
    def __init__(self, storage: str = settings.storage):
        self.storage = Path(storage)
        ensure_dir(self.storage)

    def interpolate_video(self,
                          input_video: Path,
                          out_video: Path,
                          exp: int = 2,
                          fps: Optional[int] = None,
                          scale: Literal[1,2,4] = 1,
                          fp16: bool = True) -> Path:
        """
        Use Practical-RIFE's inference_video.py for video interpolation.
        - exp: 2 => 2x frames; 3 => 4x; 4 => 8x, etc. (2^exp)
        - fps: if set, target fps; otherwise inherits input
        - scale: internal processing scale (1 or 2) for speed/quality
        """
        cmd = [
            "python3", str(RIFE_PY),
            "--exp", str(exp),
            "--input", str(input_video),
            "--output", str(out_video),
            "--scale", str(scale),
        ]
        if fps:
            cmd += ["--fps", str(fps)]
        if fp16:
            cmd += ["--fp16"]
        subprocess.run(cmd, check=True)
        return out_video

    def interpolate_two_frames(self,
                               frame_a: Path,
                               frame_b: Path,
                               out_video: Path,
                               num_mid: int = 6,
                               fps: int = 30) -> Path:
        """Interpolate N middle frames between two images and encode as video."""
        work = Path(out_video).with_suffix("").parent / (out_video.stem + "_frames")
        if work.exists():
            shutil.rmtree(work)
        ensure_dir(work)

        # prepare sequence: 000000.png (A), middle(s), 00000N.png (B)
        shutil.copy(frame_a, work / "000000.png")
        prev = work / "000000.png"

        # RIFE has a script for image pairs; invoke it in a loop creating midpoints
        # We'll use video script by composing a mini-set per pair; simplest approach:
        def rife_pair(p0: Path, p1: Path, out_dir: Path, exp: int):
            # Put two frames into a temp dir and run inference_video.py on it.
            tmp = out_dir / "pair"
            ensure_dir(tmp)
            shutil.copy(p0, tmp / "000000.png")
            shutil.copy(p1, tmp / "000001.png")
            cmd = ["python3", str(RIFE_PY), "--input", str(tmp), "--output", str(out_dir), "--exp", str(exp), "--fp16"]
            subprocess.run(cmd, check=True)
            shutil.rmtree(tmp)

        # Choose exp so that 2^exp - 1 ~= num_mid
        exp = 1
        while (2 ** exp) - 1 < num_mid:
            exp += 1

        # Run once to create dense in-betweens between A and B
        rife_pair(frame_a, frame_b, work, exp)

        # The result dir now holds 2^exp frames inclusive; rename sequentially
        frames = sorted(work.glob("*.png"))
        for idx, f in enumerate(frames):
            f.rename(work / f"{idx:06d}.png")

        encode_video_from_frames(work, out_video, fps=fps)
        return out_video