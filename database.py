"""
Base de données JSON légère pour Véronique
Gère : groupes, bannis, mutés, historique, modes
"""

import json
import os
from datetime import datetime, timedelta


DATA_DIR = "data"


class Database:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self._init_files()

    def _init_files(self):
        defaults = {
            "banned.json":   [],
            "muted.json":    {},
            "groups.json":   [],
            "history.json":  {},
            "modes.json":    {},
        }
        for filename, default in defaults.items():
            path = os.path.join(DATA_DIR, filename)
            if not os.path.exists(path):
                self._write(filename, default)

    def _read(self, filename):
        path = os.path.join(DATA_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, filename, data):
        path = os.path.join(DATA_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ── BANNISSEMENT ──────────────────────────────────────────

    def ban_user(self, phone: str):
        banned = self._read("banned.json")
        if phone not in banned:
            banned.append(phone)
            self._write("banned.json", banned)

    def unban_user(self, phone: str):
        banned = self._read("banned.json")
        banned = [b for b in banned if b != phone]
        self._write("banned.json", banned)

    def is_banned(self, phone: str) -> bool:
        return phone in self._read("banned.json")

    def get_all_banned(self) -> list:
        return self._read("banned.json")

    # ── MUTE ──────────────────────────────────────────────────

    def mute_user(self, phone: str, duration_minutes: int = 60):
        muted = self._read("muted.json")
        until = (datetime.now() + timedelta(minutes=duration_minutes)).isoformat()
        muted[phone] = until
        self._write("muted.json", muted)

    def unmute_user(self, phone: str):
        muted = self._read("muted.json")
        muted.pop(phone, None)
        self._write("muted.json", muted)

    def is_muted(self, phone: str) -> bool:
        muted = self._read("muted.json")
        if phone not in muted:
            return False
        until = datetime.fromisoformat(muted[phone])
        if datetime.now() > until:
            # Mute expiré → on le retire
            self.unmute_user(phone)
            return False
        return True

    # ── GROUPES ───────────────────────────────────────────────

    def register_group(self, group_id: str):
        groups = self._read("groups.json")
        if group_id not in groups:
            groups.append(group_id)
            self._write("groups.json", groups)

    def get_all_groups(self) -> list:
        return self._read("groups.json")

    # ── HISTORIQUE DE CONVERSATION ────────────────────────────

    def get_history(self, group_id: str, max_messages: int = 20) -> list:
        history = self._read("history.json")
        return history.get(group_id, [])[-max_messages:]

    def add_message(self, group_id: str, role: str, content: str):
        history = self._read("history.json")
        if group_id not in history:
            history[group_id] = []
        history[group_id].append({"role": role, "content": content})
        # Garder max 50 messages par groupe
        if len(history[group_id]) > 50:
            history[group_id] = history[group_id][-50:]
        self._write("history.json", history)

    def clear_group_history(self, group_id: str):
        history = self._read("history.json")
        history[group_id] = []
        self._write("history.json", history)

    # ── MODES DE GROUPE ───────────────────────────────────────

    def set_group_mode(self, group_id: str, mode: str):
        modes = self._read("modes.json")
        modes[group_id] = mode
        self._write("modes.json", modes)

    def get_group_mode(self, group_id: str) -> str:
        modes = self._read("modes.json")
        return modes.get(group_id, "libre")

    # ── RESET TOTAL ───────────────────────────────────────────

    def reset_all(self):
        self._write("banned.json",  [])
        self._write("muted.json",   {})
        self._write("groups.json",  [])
        self._write("history.json", {})
        self._write("modes.json",   {})


# Instance globale
db = Database()
