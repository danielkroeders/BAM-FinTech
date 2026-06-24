import json
import os
import sys
from pathlib import Path

PROFILE_FILENAME = "local_server.json"


def llm_models_dir():
    override = os.getenv("CREDRISK_LLM_MODELS_DIR")
    if override:
        return Path(override).expanduser()

    if os.name == "nt":
        local_app_data = os.getenv("LOCALAPPDATA")
        base_dir = (
            Path(local_app_data)
            if local_app_data
            else Path.home() / "AppData" / "Local"
        )
        return base_dir / "CredRiskAI" / "llm_models"

    if sys.platform == "darwin":
        return (
            Path.home()
            / "Library"
            / "Application Support"
            / "CredRiskAI"
            / "llm_models"
        )

    config_home = os.getenv("XDG_CONFIG_HOME")
    base_dir = (
        Path(config_home).expanduser() if config_home else Path.home() / ".config"
    )
    return base_dir / "CredRiskAI" / "llm_models"


def local_llm_profile_path():
    return llm_models_dir() / PROFILE_FILENAME


def load_local_llm_profile():
    path = local_llm_profile_path()
    if not path.exists():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    return {
        "ip": str(payload.get("ip", "")).strip(),
        "model_name": str(payload.get("model_name", "")).strip(),
    }


def save_local_llm_profile(ip, model_name):
    ip = (ip or "").strip()
    model_name = (model_name or "").strip()
    if not ip or not model_name:
        raise ValueError("Local server URL/IP and model name are required.")

    directory = llm_models_dir()
    directory.mkdir(parents=True, exist_ok=True)
    try:
        directory.chmod(0o700)
    except OSError:
        pass

    path = local_llm_profile_path()
    temp_path = path.with_suffix(".tmp")
    payload = {"ip": ip, "model_name": model_name}
    temp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temp_path.replace(path)
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return path
