# -*- coding: utf-8 -*-
from __future__ import annotations
import logging
from typing import Literal

Status = Literal["initial", "no_change", "changed", "error"]

def notify(status: Status, url: str) -> None:
    """
    Hook d'alerte minimal :
      - 'changed'  -> WARNING immédiat
      - 'initial'  -> INFO
      - 'no_change'-> INFO
      - 'error'    -> ERROR
    Évolution : envoyer un mail (smtplib), Slack/Discord webhook, etc.
    """
    if status == "changed":
        logging.warning("[ALERTE] Changement détecté sur %s", url)
    elif status == "initial":
        logging.info("Référence initiale enregistrée pour %s", url)
    elif status == "no_change":
        logging.info("Aucun changement pour %s", url)
    elif status == "error":
        logging.error("Erreur lors de la vérification de %s", url)
