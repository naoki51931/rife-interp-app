# /app/utils/video.py
# ============================================================
# ffmpegを用いたフレーム抽出・動画化ユーティリティ
# Practical-RIFE + FastAPI 環境対応版（glob対応付き）
# ============================================================

import os
import subprocess
from pathlib import Path


def ensure_dir(path: Path):
    """指定ディレクトリが存在しない場合に作成"""
    os.makedirs(path, exist_ok=True)


def extract_frames(video_path: Path, out_dir: Path, fps: int = 30):
    """動画ファイルから指定FPSでフレームを抽出"""
    ensure_dir(out_dir)
    cmd = [
        "ffmpeg",
        "-nostdin",
        "-y",
        "-i", str(video_path),
        "-vf", f"fps={fps}",
        str(out_dir / "%06d.png"),
    ]
    print("🎥 Extracting frames:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def encode_video_from_frames(frame_dir: Path, output_path: Path, fps: int = 30):
    """
    ffmpegで指定ディレクトリ内の連番画像(%06d.png)を動画化
    例：000001.png, 000002.png … のように連番で保存されている場合
    """
    cmd = [
        "ffmpeg",
        "-nostdin",
        "-y",
        "-framerate", str(fps),
        "-i", str(frame_dir / "%06d.png"),
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        str(output_path),
    ]
    print("🎬 Encoding (sequential):", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"✅ 動画生成完了: {output_path}")


def encode_video_from_frames_glob(frame_dir: Path, output_path: Path, fps: int = 30):
    """
    ffmpegでワイルドカード(*.png)を使って動画化（glob対応）
    ファイル名に_が含まれていたり、連番でない場合に有効
    """
    ensure_dir(frame_dir)
    cmd = [
        "ffmpeg",
        "-nostdin",
        "-y",
        "-framerate", str(fps),
        "-pattern_type", "glob",
        "-i", str(frame_dir / "*.png"),
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        str(output_path),
    ]
    print("🎬 Encoding (glob):", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"✅ 動画生成完了: {output_path}")


def auto_encode_video(frame_dir: Path, output_path: Path, fps: int = 30):
    """
    自動判定で encode_video_from_frames / glob を選択
    000001.png が存在すれば連番モード、それ以外はglobモード
    """
    sequential_first = frame_dir / "000001.png"
    if sequential_first.exists():
        print("🧩 Detected sequential frames → using %06d mode")
        encode_video_from_frames(frame_dir, output_path, fps)
    else:
        print("🧩 Detected irregular frame names → using glob mode")
        encode_video_from_frames_glob(frame_dir, output_path, fps)
