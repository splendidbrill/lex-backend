import json
import os
from typing import Any, Dict, Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def save_user_artifact(table: str, user_id: str, data: Dict[str, Any]) -> None:
    table_dir = os.path.abspath(os.path.join(DATA_DIR, table))
    _ensure_dir(table_dir)
    file_path = os.path.join(table_dir, f"{user_id}.json")
    try:
        payload = {"user_id": user_id, **data}
        # If exists, append history list
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            history = existing.get("history", [])
        else:
            history = []
        history.append(payload)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"history": history}, f, ensure_ascii=False, indent=2)
    except Exception:
        # best-effort
        pass


def get_latest_user_artifact(table: str, user_id: str) -> Optional[Dict[str, Any]]:
    table_dir = os.path.abspath(os.path.join(DATA_DIR, table))
    file_path = os.path.join(table_dir, f"{user_id}.json")
    try:
        if not os.path.exists(file_path):
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        history = payload.get("history", [])
        if not history:
            return None
        return history[-1]
    except Exception:
        return None
