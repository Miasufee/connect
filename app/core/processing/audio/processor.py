import subprocess
import tempfile
from pathlib import Path


class AudioProcessor:
    """
    High-performance audio processing using FFmpeg.
    """

    @staticmethod
    def _run_ffmpeg(args: list[str]) -> bytes:
        proc = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return proc.stdout

    @staticmethod
    def transcode(
        audio_bytes: bytes,
        input_ext: str,
        output_ext: str,
        bitrate: str = "192k",
    ) -> bytes:
        with tempfile.NamedTemporaryFile(suffix=f".{input_ext}") as src, \
             tempfile.NamedTemporaryFile(suffix=f".{output_ext}") as dst:

            src.write(audio_bytes)
            src.flush()

            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i", src.name,
                    "-vn",
                    "-acodec", output_ext,
                    "-ab", bitrate,
                    dst.name,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )

            return dst.read()

    @staticmethod
    def trim(
        audio_bytes: bytes,
        input_ext: str,
        start: float,
        end: float | None = None,
    ) -> bytes:
        with tempfile.NamedTemporaryFile(suffix=f".{input_ext}") as src, \
             tempfile.NamedTemporaryFile(suffix=f".{input_ext}") as dst:

            src.write(audio_bytes)
            src.flush()

            args = [
                "ffmpeg", "-y",
                "-ss", str(start),
                "-i", src.name,
            ]

            if end:
                args += ["-to", str(end)]

            args += ["-c", "copy", dst.name]

            subprocess.run(args, check=True)
            return dst.read()

    @staticmethod
    def normalize(audio_bytes: bytes, input_ext: str) -> bytes:
        with tempfile.NamedTemporaryFile(suffix=f".{input_ext}") as src, \
             tempfile.NamedTemporaryFile(suffix=f".{input_ext}") as dst:

            src.write(audio_bytes)
            src.flush()

            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i", src.name,
                    "-af", "loudnorm",
                    dst.name,
                ],
                check=True,
            )

            return dst.read()
