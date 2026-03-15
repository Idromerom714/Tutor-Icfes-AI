import os
import re

import streamlit as st
import streamlit.components.v1 as components

ADSENSE_JS_URL = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"
DEFAULT_CLIENT_ID = "ca-pub-5888906096884160"


def _read_setting(name: str, default: str = "") -> str:
    env_value = os.getenv(name)
    if env_value not in (None, ""):
        return str(env_value).strip()

    try:
        secret_value = st.secrets.get(name, default)
    except Exception:
        secret_value = default

    return str(secret_value).strip() if secret_value is not None else ""


def _is_enabled() -> bool:
    raw = _read_setting("ADSENSE_ENABLED", "true").lower()
    return raw not in {"0", "false", "no", "off"}


def _normalize_client_id(client_id: str) -> str:
    cid = (client_id or "").strip()
    if cid.startswith("ca-pub-"):
        return cid
    if cid.startswith("pub-"):
        return f"ca-{cid}"
    return cid


def _normalize_slot_id(slot_id: str) -> str:
    return re.sub(r"\D", "", slot_id or "")


def get_adsense_client_id() -> str:
    configured = _read_setting("ADSENSE_CLIENT_ID", DEFAULT_CLIENT_ID)
    return _normalize_client_id(configured)


def render_adsense_slot(slot_id: str, min_height: int = 140) -> bool:
    if not _is_enabled():
        return False

    client_id = get_adsense_client_id()
    slot = _normalize_slot_id(slot_id)

    if not client_id or not slot:
        return False

    ad_html = f"""
<div style=\"width:100%; min-height:{max(min_height, 100)}px;\">
  <script async src=\"{ADSENSE_JS_URL}?client={client_id}\" crossorigin=\"anonymous\"></script>
  <ins class=\"adsbygoogle\"
      style=\"display:block; text-align:center;\"
      data-ad-client=\"{client_id}\"
      data-ad-slot=\"{slot}\"
      data-ad-format=\"auto\"
      data-full-width-responsive=\"true\"></ins>
  <script>
      (adsbygoogle = window.adsbygoogle || []).push({{}});
  </script>
</div>
"""
    components.html(ad_html, height=max(min_height, 100), scrolling=False)
    return True


def render_adsense_slot_from_env(setting_name: str, min_height: int = 140) -> bool:
    slot = _read_setting(setting_name)
    if not slot:
        slot = _read_setting("ADSENSE_SLOT_DEFAULT")
    return render_adsense_slot(slot, min_height=min_height)
