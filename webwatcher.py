#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import argparse
import contextlib
import logging
import signal
import sys
import time
from pathlib import Path
from typing import Optional, List

# Import du cœur applicatif
from core.fetcher import fetch_page
from core.sanitizer import sanitize_html
from core.hasher import compute_hash
from core.storage import (
    configure_logging,
    load_state,
    save_state,
    init_history,
    write_history,
    utc_now_iso,
)

def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="webwatcher",
        description="Surveille une page web et alerte sur modification (POC modulaire).",
    )
    p.add_argument("--url", required=True, help="URL à surveiller (ex: https://example.com)")
    p.add_argument("--interval", type=int, help="Intervalle en secondes (si absent: exécution unique)")
    p.add_argument("--state", default="data/state.json", help="Chemin du fichier d'état JSON")
    p.add_argument("--timeout", type=int, default=10, help="Timeout HTTP en secondes (défaut: 10)")
    p.add_argument("--user-agent", default="WebWatcher/1.0 (+contact)", help="User-Agent explicite")
    p.add_argument("--log-level", default="INFO", help="Niveau logs: DEBUG/INFO/WARNING/ERROR")
    p.add_argument("--log-file", default=None, help="Chemin de fichier de logs (optionnel)")
    p.add_argument("--selector", default=None, help="CSS selector pour cibler une zone (ex: 'main')")
    p.add_argument("--ignore", default=None, help="Sélecteurs à ignorer, séparés par des virgules (ex: '.banner,.ads')")
    p.add_argument("--history", default=None, help="SQLite pour l'historique (ex: data/history.sqlite)")
    p.add_argument("--backoff", action="store_true", help="Active un backoff simple en cas d'erreurs réseau")
    return p.parse_args(argv)

def compare_and_label(prev_hash: Optional[str], new_hash: str) -> str:
    """
    Retourne un label de statut et journalise :
      - 'initial'    si pas d’état précédent
      - 'no_change'  si hash identique
      - 'changed'    sinon (alerte)
    """
    if not prev_hash:
        logging.info("Première exécution : référence enregistrée.")
        return "initial"
    if prev_hash == new_hash:
        logging.info("Aucun changement détecté.")
        return "no_change"
    logging.warning("*** ALERTE *** Changement détecté.")
    return "changed"

def main(argv=None) -> int:
    args = parse_args(argv)
    configure_logging(args.log_level, args.log_file)

    # Prépare l'historique si demandé
    history_db = Path(args.history) if args.history else None
    if history_db:
        init_history(history_db)

    # Parse des sélecteurs à ignorer
    ignore_selectors: Optional[List[str]] = (
        [s.strip() for s in args.ignore.split(",")] if args.ignore else None
    )

    # Gestion arrêt propre (Ctrl-C / kill)
    stop = {"flag": False}
    def _sig_handler(signum, _frame):
        stop["flag"] = True
        logging.info("Signal %s reçu : arrêt propre...", signum)
    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(Exception):
            signal.signal(sig, _sig_handler)

    state_path = Path(args.state)
    interval = args.interval
    next_interval = interval or 0
    max_interval = int((interval or 1) * 10) if interval else 0

    while True:
        fr = fetch_page(args.url, args.timeout, args.user_agent)
        if fr.error:
            logging.error("Échec récupération %s : %s", args.url, fr.error)
            if history_db:
                write_history(
                    history_db, url=args.url, status="error", hash_value=None,
                    http_status=fr.status_code, content_length=fr.content_length, note=fr.error
                )
        else:
            logging.info("Fetch %s (%s, %s bytes)", args.url, fr.status_code, fr.content_length or 0)
            processed = sanitize_html(fr.text or "", args.selector, ignore_selectors)
            h = compute_hash(processed)

            state = load_state(state_path)
            prev_hash = state.get("hash")
            status = compare_and_label(prev_hash, h)

            if history_db:
                write_history(
                    history_db, url=args.url, status=status, hash_value=h,
                    http_status=fr.status_code, content_length=fr.content_length, note=None
                )

            # Mise à jour de l'état sur succès
            new_state = {
                "url": args.url,
                "hash": h,
                "updated_at": utc_now_iso(),
                "selector": args.selector,
                "ignore": ignore_selectors,
                "last_http_status": fr.status_code,
                "last_content_length": fr.content_length,
                "user_agent": args.user_agent,
            }
            save_state(state_path, new_state)

        # Sorties de boucle
        if interval is None or stop["flag"]:
            break

        # Attente avant itération suivante
        sleep_for = next_interval if next_interval > 0 else interval
        try:
            time.sleep(sleep_for)
        except KeyboardInterrupt:
            logging.info("Interruption utilisateur, arrêt.")
            break

        # Backoff progressif sur erreurs (simple, plafonné)
        if args.backoff and fr.error:
            next_interval = min(int(sleep_for * 1.5), max_interval)  # +50% jusqu’à 10x
        else:
            next_interval = interval  # reset si succès ou backoff désactivé

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
