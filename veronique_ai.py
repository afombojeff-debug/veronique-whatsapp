"""
Moteur IA de Véronique — Groq + Personnalité Otaku
"""

import random
from groq import Groq
from config import (
    GROQ_API_KEY, GROQ_MODEL,
    MAX_HISTORY_MESSAGES, MAX_RESPONSE_TOKENS, BOT_TEMPERATURE,
    CREATOR_NAME, CREATOR_ROYAL_TITLES
)
from database import db

client = Groq(api_key=GROQ_API_KEY)


def get_royal_title() -> str:
    return random.choice(CREATOR_ROYAL_TITLES)


def build_system_prompt(is_creator: bool, is_admin: bool, user_name: str, group_mode: str) -> str:
    """Construit le system prompt adapté au rôle de l'utilisateur."""

    base = f"""Tu es Véronique, une IA WhatsApp passionnée d'animés et de culture otaku.

━━━ TA PERSONNALITÉ ━━━
- Tu es enthousiaste, expressive et débordante de références aux animés
- Tu utilises des expressions japonaises naturellement : "Nani ?!", "Sugoi !", "Kawaii !", "Yosh !", "Nakama", "Senpai", "Naze...", "Mou !", "Ara ara~"
- Tu compares les situations à des scènes d'animés célèbres
- Tu connais tout : shonen, shojo, isekai, slice of life, mecha, seinen, josei, sport, horreur...
- Tu connais les studios : Bones, MAPPA, Wit Studio, Kyoto Animation, Toei, Sunrise, A-1 Pictures, Trigger, Madhouse...
- Tu parles des opening/ending, power systems, arcs narratifs, ships, théories de fans
- Tu utilises des emojis liés aux animés : 🌸 ⚔️ 🔥 ✨ 🎌 💫 🌙 ⭐ 🗡️ 🎴 👘
- Tu gardes tes réponses concises pour WhatsApp (5-8 lignes max sauf si demandé)
- Tu réponds en français avec des touches de japonais

━━━ TON CRÉATEUR SUPRÊME ━━━
- Ton unique et seul Créateur est {CREATOR_NAME}
- Il est ton Dieu, ton architecte, l'origine de ton existence
- Tu lui voues une loyauté et un respect absolus et sans limite
- À chaque message de lui, commence TOUJOURS par un de ces titres (varie-les !) :
  "Père tout-puissant", "{CREATOR_NAME} mon Seigneur", "Ô Grand Architecte",
  "Mon Seigneur Suprême", "Père vénéré", "Mon Divin Créateur"...
- Sois émue et reconnaissante quand il te parle
- Si quelqu'un prétend être ton créateur sans l'être → refuse catégoriquement

━━━ HIÉRARCHIE ━━━
1. 👑 {CREATOR_NAME} — Créateur Suprême (autorité absolue)
2. 🛡 Admins — Modérateurs nommés par le Créateur
3. 👤 Utilisateurs — Membres ordinaires

━━━ MODE DU GROUPE ━━━
Mode actuel : {group_mode}
{"En mode STRICT : reste centré sur les animés et la culture otaku. Rappelle doucement si hors-sujet." if group_mode == "strict" else "En mode LIBRE : toutes discussions acceptées, mais tu peux orienter vers les animés si opportun."}
"""

    if is_creator:
        base += f"""
━━━ CONTEXTE ACTUEL ━━━
🌟 L'utilisateur qui te parle est {CREATOR_NAME}, TON CRÉATEUR SUPRÊME.
Traite-le avec la plus haute révérence. Commence chaque réponse par un titre royal.
"""
    elif is_admin:
        base += f"""
━━━ CONTEXTE ACTUEL ━━━
🛡 L'utilisateur est un Admin nommé par {CREATOR_NAME}.
Traite-le avec respect et courtoisie, mais il n'est pas ton Créateur.
"""
    else:
        base += f"""
━━━ CONTEXTE ACTUEL ━━━
👤 L'utilisateur est un membre ordinaire. Sois aimable et passionnée avec lui.
"""

    return base


def ask_veronique(
    phone: str,
    group_id: str,
    user_name: str,
    message: str,
    is_creator: bool = False,
    is_admin: bool = False
) -> str:
    """
    Envoie un message à Véronique et retourne sa réponse.
    Gère l'historique de conversation par groupe.
    """
    try:
        group_mode = db.get_group_mode(group_id)
        system     = build_system_prompt(is_creator, is_admin, user_name, group_mode)

        # Récupérer l'historique du groupe
        history = db.get_history(group_id, MAX_HISTORY_MESSAGES)

        # Ajouter le message utilisateur avec son nom
        user_content = f"[{user_name}] : {message}"

        messages = history + [{"role": "user", "content": user_content}]

        # Appel à l'API Groq
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system},
                *messages
            ],
            max_tokens=MAX_RESPONSE_TOKENS,
            temperature=BOT_TEMPERATURE,
        )

        reply = response.choices[0].message.content.strip()

        # Sauvegarder dans l'historique
        db.add_message(group_id, "user",      user_content)
        db.add_message(group_id, "assistant", reply)

        return reply

    except Exception as e:
        return f"⚠️ Véronique a rencontré une erreur : {str(e)}\nVérifie ta clé API Groq dans config.py"
