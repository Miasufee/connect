import subprocess
import json
import tempfile


class AudioAnalyzer:
    @staticmethod
    def probe(audio_bytes: bytes, ext: str) -> dict:
        with tempfile.NamedTemporaryFile(suffix=f".{ext}") as f:
            f.write(audio_bytes)
            f.flush()

            result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "error",
                    "-show_entries",
                    "format=duration,bit_rate",
                    "-show_streams",
                    "-of", "json",
                    f.name,
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            return json.loads(result.stdout)
