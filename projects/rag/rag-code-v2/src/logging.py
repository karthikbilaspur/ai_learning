import json, logging, sys, time
from typing import Any

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload={"timestamp":time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)), "level":record.levelname, "logger":record.name, "message":record.getMessage()}
        if hasattr(record, "extra_data"): payload.update(record.extra_data)
        return json.dumps(payload, default=str)

def configure_logging(level: str="INFO") -> None:
    handler=logging.StreamHandler(sys.stdout); handler.setFormatter(JsonFormatter())
    root=logging.getLogger(); root.handlers.clear(); root.addHandler(handler); root.setLevel(level.upper())

def log(logger: logging.Logger, level: int, message: str, **data: Any) -> None:
    logger.log(level, message, extra={"extra_data":data})
