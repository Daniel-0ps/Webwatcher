# -*- coding: utf-8 -*-
from __future__ import annotations
import logging
from typing import Optional, List

try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception:  # pragma: no cover
    BeautifulSoup = None  # type: ignore

def sanitize_html(html: str, selector: Optional[str], ignore_selectors: Optional[List[str]]) -> str:
    """
    Réduit le bruit (pubs, bandeaux dynamiques, timestamps).
    - Sans BeautifulSoup -> retourne HTML brut + warning.
    - selector -> n'observe qu'une sous-partie.
    - ignore_selectors -> supprime ces blocs avant extraction texte.
    Retourne du TEXTE (get_text) pour limiter les diffs de markup.
    """
    if not selector and not ignore_selectors:
        return html
    if BeautifulSoup is None:
        logging.warning("beautifulsoup4 non installé ; filtrage ignoré.")
        return html

    soup = BeautifulSoup(html, "html.parser")
    root = soup
    if selector:
        sel = soup.select_one(selector)
        if sel is None:
            logging.warning("Sélecteur '%s' introuvable ; document entier utilisé.", selector)
        else:
            root = sel

    if ignore_selectors:
        for ign in ignore_selectors:
            for tag in root.select(ign):
                tag.decompose()

    text = root.get_text(separator="\n", strip=True)
    return text
