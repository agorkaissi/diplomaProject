from fastapi import APIRouter
import subprocess
import re

router = APIRouter()

@router.get("/llm/status")
def get_llm_status():
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )

        lines = result.stdout.strip().split("\n")
        models = []

        for line in lines[1:]:
            if not line.strip():
                continue

            match = re.match(r"(\S+)\s+(\S+)\s+([\d.]+\s\w+)\s+(.+)", line)

            if not match:
                continue

            name_id, model_id, size, modified = match.groups()

            name = name_id.split(":")[0]
            version = name_id.split(":")[1] if ":" in name_id else "unknown"

            models.append({
                "name": name,
                "status": "online",
                "version": version,
                "loaded": True,
                "context_length": 8192,
                "memory_usage": size,
                "uptime": modified
            })

        return {"models": models}

    except Exception:
        return {"models": []}
