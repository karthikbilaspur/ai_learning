
import os, pathlib, time
import structlog
from PIL import Image

logger = structlog.get_logger()

ALLOWED_DIR = pathlib.Path("/app/data")
ALLOWED_DIR.mkdir(exist_ok=True)

def rename_files(params: dict):
    logger.info("tool_start", tool="rename_files")
    pattern = params.get("pattern", "file_{i}")
    directory = pathlib.Path(params.get("directory", str(ALLOWED_DIR)))
    # Security: allowlist
    if not str(directory.resolve()).startswith(str(ALLOWED_DIR.resolve())):
        raise ValueError("Directory outside allowed path")
    files = list(directory.glob("*"))
    renamed = []
    for i, f in enumerate(files):
        if f.is_file():
            new_name = pattern.format(i=i, name=f.stem)
            new_path = f.parent / f"{new_name}{f.suffix}"
            # f.rename(new_path)  # disabled for safety in demo
            renamed.append(str(new_path))
    return {"renamed_count": len(renamed), "preview": renamed[:10]}

def rename_with_time(params: dict):
    logger.info("tool_start", tool="rename_with_time")
    directory = pathlib.Path(params.get("directory", str(ALLOWED_DIR)))
    if not str(directory.resolve()).startswith(str(ALLOWED_DIR.resolve())):
        raise ValueError("Directory outside allowed path")
    return {"mode": "time_prefix", "directory": str(directory), "example": "2026-08-22_file.txt"}

def rescale_image(params: dict):
    logger.info("tool_start", tool="rescale_image")
    width = int(params.get("width", 512))
    height = int(params.get("height", 512))
    # Demo: would open image via PIL
    return {"rescaled_to": f"{width}x{height}", "note": "Upload image to /app/data and call with filename"}
