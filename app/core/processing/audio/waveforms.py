import subprocess
import tempfile


class WaveformGenerator:
    @staticmethod
    def generate(audio_bytes: bytes, input_ext: str) -> bytes:
        with tempfile.NamedTemporaryFile(suffix=f".{input_ext}") as src, \
             tempfile.NamedTemporaryFile(suffix=".png") as out:

            src.write(audio_bytes)
            src.flush()

            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i", src.name,
                    "-filter_complex",
                    "aformat=channel_layouts=mono,showwavespic=s=800x200",
                    out.name,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )

            return out.read()
