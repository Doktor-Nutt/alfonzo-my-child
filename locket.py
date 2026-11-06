# locket.py
import asyncio
import shutil
import tempfile
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"


async def makesweet(template: str, images: list[bytes], timeout: float = 60) -> bytes:
    """Render a makesweet template with the given images (PNG/JPG bytes). Returns GIF bytes."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        shutil.copy(TEMPLATES_DIR / template, tmp / template)

        names = []
        for i, data in enumerate(images):
            name = f"in{i}.png"
            (tmp / name).write_bytes(data)
            names.append(name)

        proc = await asyncio.create_subprocess_exec(
            "docker", "run", "--rm",
            "-v", f"{tmp}:/share",
            "paulfitz/makesweet",
            "--zip", template,
            "--in", *names,
            "--gif", "out.gif",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            _, err = await asyncio.wait_for(proc.communicate(), timeout)
        except asyncio.TimeoutError:
            proc.kill()
            raise RuntimeError("makesweet timed out")

        out = tmp / "out.gif"
        if proc.returncode != 0 or not out.exists():
            raise RuntimeError(f"makesweet failed: {err.decode(errors='ignore')}")
        return out.read_bytes()
