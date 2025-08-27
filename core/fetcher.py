# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

try:
    import requests
except Exception:  # pragma: no cover
    requests = None  # type: ignore

@dataclass
class FetchResult:
    text: Optional[str]
    status_code: Optional[int]
    content_length: Optional[int]
    error: Optional[str]

def fetch_page(url: str, timeout: int, user_agent: Optional[str]) -> FetchResult:
    """
    GET sur l'URL cible, avec User-Agent explicite et timeout.
    - Succès (200) -> texte décodé (UTF-8 par défaut).
    - Erreur -> error renseigné, pas d'état modifié côté appelant.
    """
    if requests is None:
        return FetchResult(None, None, None, "Dépendance manquante: requests. pip install requests")

    headers = {}
    if user_agent:
        headers["User-Agent"] = user_agent

    try:
        resp = requests.get(url, headers=headers, timeout=timeout)  # verify=True par défaut
        status = resp.status_code
        content_length = len(resp.content or b"")
        if status != 200:
            return FetchResult(None, status, content_length, f"HTTP {status}")
        resp.encoding = resp.encoding or "utf-8"
        return FetchResult(resp.text, status, content_length, None)
    except requests.exceptions.Timeout:
        return FetchResult(None, None, None, f"Timeout après {timeout}s")
    except requests.exceptions.RequestException as e:
        return FetchResult(None, None, None, str(e))
