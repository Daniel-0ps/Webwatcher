# -*- coding: utf-8 -*-
from __future__ import annotations
import hashlib

def normalize_text(text: str) -> str:
    """
    Normalise pour réduire les faux positifs :
      - CRLF -> LF
      - trim + réduction des espaces multiples
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    collapsed = " ".join(text.split())
    return collapsed.strip()

def compute_hash(text: str) -> str:
    normalized = normalize_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
