
import os, pathlib, shutil
from datetime import datetime
import structlog

logger = structlog.get_logger()
ALLOWED_DIR = pathlib.Path("/app/data")
ALLOWED_DIR.mkdir(exist_ok=True)

def _safe_dir(directory: str) -> pathlib.Path:
    p = pathlib.Path(directory).resolve()
    allowed = ALLOWED_DIR.resolve()
    # allow subdirs of ALLOWED_DIR or ALLOWED_DIR itself
    if not str(p).startswith(str(allowed)):
        raise ValueError(f"Directory {directory} outside allowed path {allowed}. Use /app/data")
    p.mkdir(parents=True, exist_ok=True)
    return p

# ---- YOUR ORIGINAL LOGIC PRESERVED ----

def rename_files_original(directory: str, old_name: str, new_name: str, languages: list):
    # With translation
    try:
        from googletrans import Translator
        translator = Translator()
        use_trans = True
    except ImportError:
        use_trans = False

    dir_path = _safe_dir(directory)
    renamed = []
    for filename in os.listdir(dir_path):
        if old_name in filename:
            file_extension = os.path.splitext(filename)[1]
            if use_trans and languages:
                for language in languages:
                    try:
                        translation = translator.translate(new_name, dest=language)
                        new_filename = filename.replace(old_name, translation.text)
                        src = dir_path / filename
                        dst = dir_path / new_filename
                        shutil.copy(src, dst)
                        renamed.append(str(dst))
                        logger.info("renamed", src=str(src), dst=str(dst), lang=language)
                    except Exception as e:
                        logger.warning("translation_failed", lang=language, error=str(e))
            else:
                new_filename = filename.replace(old_name, new_name)
                src = dir_path / filename
                dst = dir_path / new_filename
                os.rename(src, dst)
                renamed.append(str(dst))
    return renamed

def rename_with_time_original(directory: str, old_name: str, new_name: str, languages: list = None):
    dir_path = _safe_dir(directory)
    renamed = []
    for filename in os.listdir(dir_path):
        if old_name in filename:
            new_filename = filename.replace(old_name, new_name)
            src = dir_path / filename
            dst = dir_path / new_filename
            os.rename(src, dst)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info("renamed_with_time", src=str(src), dst=str(dst), time=current_time)
            renamed.append({"file": str(dst), "time": current_time})
    return renamed

def rename_without_translation(directory: str, old_name: str, new_name: str):
    dir_path = _safe_dir(directory)
    renamed = []
    for filename in os.listdir(dir_path):
        if old_name in filename:
            new_filename = filename.replace(old_name, new_name)
            os.rename(dir_path / filename, dir_path / new_filename)
            renamed.append(new_filename)
    return renamed

def rescale_image_original(image_path: str, new_size: tuple):
    from PIL import Image
    img_path = pathlib.Path(image_path)
    # allow only inside ALLOWED_DIR
    if not str(img_path.resolve()).startswith(str(ALLOWED_DIR.resolve())):
        # if not allowed, try to find in ALLOWED_DIR
        img_path = ALLOWED_DIR / img_path.name
    img = Image.open(img_path)
    img = img.resize(new_size)
    output = ALLOWED_DIR / "rescaled_image.jpg"
    img.save(output)
    logger.info("image_rescaled", input=str(img_path), output=str(output), size=new_size)
    return str(output)

# ---- AGENT WRAPPERS ----
def rename_files(params: dict):
    logger.info("tool_start", tool="rename_files", params=params)
    directory = params.get("directory", "/app/data")
    old = params.get("old_name","")
    new = params.get("new_name","")
    langs = params.get("languages", [])
    if not old or not new:
        raise ValueError("old_name and new_name required")
    result = rename_files_original(directory, old, new, langs)
    return {"renamed_count": len(result), "files": result[:20]}

def rename_with_time(params: dict):
    logger.info("tool_start", tool="rename_with_time", params=params)
    directory = params.get("directory", "/app/data")
    old = params.get("old_name","")
    new = params.get("new_name","")
    result = rename_with_time_original(directory, old, new)
    return {"renamed": result}

def rescale_image(params: dict):
    logger.info("tool_start", tool="rescale_image", params=params)
    image_path = params.get("image_path", "/app/data/sample.jpg")
    width = int(params.get("width", 512))
    height = int(params.get("height", 512))
    output = rescale_image_original(image_path, (width, height))
    return {"output": output, "size": f"{width}x{height}"}
