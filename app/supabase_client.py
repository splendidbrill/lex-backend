from typing import Any, Dict, Optional

try:
	from supabase import create_client, Client
except Exception:  # pragma: no cover
	create_client = None  # type: ignore
	Client = object  # type: ignore

from .config import get_settings
from .fs_storage import save_user_artifact as fs_save, get_latest_user_artifact as fs_get_latest


def get_supabase() -> Optional["Client"]:
	settings = get_settings()
	if not settings.supabase_url or not settings.supabase_key or not create_client:
		return None
	return create_client(settings.supabase_url, settings.supabase_key)


def insert_user_artifact(table: str, user_id: str, data: Dict[str, Any]) -> None:
	sb = get_supabase()
	if not sb:
		fs_save(table, user_id, data)
		return
	payload = {"user_id": user_id, **data}
	try:
		sb.table(table).insert(payload).execute()
	except Exception:
		fs_save(table, user_id, data)


def get_latest_artifact(table: str, user_id: str) -> Optional[Dict[str, Any]]:
	sb = get_supabase()
	if not sb:
		return fs_get_latest(table, user_id)
	try:
		res = sb.table(table).select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
		if hasattr(res, "data") and res.data:
			return res.data[0]
	except Exception:
		pass
	return fs_get_latest(table, user_id)
