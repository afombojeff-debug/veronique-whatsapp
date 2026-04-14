"""
Module d'authentification — Créateur & Admins
"""

import json
import os
from config import CREATOR_PHONES, CREATOR_DISPLAY_NAMES, CREATOR_TITLE

ADMINS_FILE = "data/admins.json"


def _load_admins():
    if not os.path.exists(ADMINS_FILE):
        return []
    with open(ADMINS_FILE, "r") as f:
        return json.load(f)


def _save_admins(admins):
    os.makedirs("data", exist_ok=True)
    with open(ADMINS_FILE, "w") as f:
        json.dump(admins, f, indent=2)


def _normalize(phone: str) -> str:
    """Normalise un numéro de téléphone pour la comparaison."""
    return phone.replace("+", "").replace(" ", "").replace("-", "").strip()


def is_creator(phone: str, display_name: str = "") -> bool:
    """
    Vérifie si l'utilisateur est Jeff Afombo Mbarga, le Créateur Suprême.
    Vérification par numéro ET par nom d'affichage.
    """
    norm_phone = _normalize(phone)

    # Vérification par numéro
    for cp in CREATOR_PHONES:
        if _normalize(cp) in norm_phone or norm_phone in _normalize(cp):
            return True

    # Vérification par nom d'affichage (sécurité secondaire)
    if display_name:
        for name in CREATOR_DISPLAY_NAMES:
            if name.lower() in display_name.lower():
                return True

    return False


def is_admin(phone: str) -> bool:
    """Vérifie si l'utilisateur est admin."""
    admins = _load_admins()
    norm_phone = _normalize(phone)
    return any(_normalize(a) == norm_phone for a in admins)


def add_admin(phone: str) -> bool:
    """Ajoute un admin."""
    admins = _load_admins()
    norm = _normalize(phone)
    if not any(_normalize(a) == norm for a in admins):
        admins.append(phone)
        _save_admins(admins)
        return True
    return False


def remove_admin(phone: str) -> bool:
    """Retire un admin."""
    admins = _load_admins()
    norm = _normalize(phone)
    new_admins = [a for a in admins if _normalize(a) != norm]
    if len(new_admins) < len(admins):
        _save_admins(new_admins)
        return True
    return False


def list_admins() -> list:
    """Liste tous les admins."""
    return _load_admins()
