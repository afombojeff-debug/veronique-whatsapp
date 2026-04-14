"""
╔══════════════════════════════════════════════════════════════╗
║        VÉRONIQUE — Bot WhatsApp Otaku via Twilio             ║
║    Créée pour et par Jeff Afombo Mbarga — Créateur Suprême   ║
╚══════════════════════════════════════════════════════════════╝
"""

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import re
from config import *
from auth import is_creator, is_admin, add_admin, remove_admin, list_admins
from veronique_ai import ask_veronique
from database import db

app = Flask(__name__)

# ──────────────────────────────────────────────
#  COMMANDES DISPONIBLES
# ──────────────────────────────────────────────

CREATOR_COMMANDS = """
╔══ ⚜ COMMANDES CRÉATEUR ⚜ ══╗
/attrib-admin @num  → Donner le rôle admin
/retirer-admin @num → Retirer le rôle admin
/liste-admins       → Voir tous les admins
/exit               → Éteindre Véronique
/broadcast <msg>    → Envoyer à tous les groupes
/reset-mem          → Réinitialiser toute la mémoire
/statut             → Voir le statut complet du bot
╚════════════════════════════╝"""

ADMIN_COMMANDS = """
╔══ 🛡 COMMANDES ADMIN 🛡 ══╗
/ban @num           → Bannir un utilisateur
/unban @num         → Débannir un utilisateur
/mute @num          → Réduire au silence (1h)
/unmute @num        → Lever le silence
/liste-bannis       → Voir les bannis
/clear              → Effacer mémoire du groupe
/annonce <msg>      → Annoncer dans le groupe
/mode-strict        → Activer modération stricte
/mode-libre         → Désactiver modération stricte
╚═══════════════════════════╝"""

USER_COMMANDS = """
╔══ 🌸 COMMANDES 🌸 ══╗
/aide           → Ce menu
/animes         → Top animés de Véronique
/recommande     → Recommandation personnalisée
/quiz           → Quiz animé surprise
/waifu          → Waifu aléatoire du jour
/quote          → Citation d'animé
╚═════════════════════╝"""


# ──────────────────────────────────────────────
#  GESTIONNAIRE PRINCIPAL DES MESSAGES
# ──────────────────────────────────────────────

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    sender       = request.values.get("From", "")       # whatsapp:+237XXXXXXXX
    group_id     = request.values.get("To", sender)     # ID du groupe ou du bot
    sender_name  = request.values.get("ProfileName", "Inconnu")

    phone = sender.replace("whatsapp:", "").strip()

    resp = MessagingResponse()
    msg  = resp.message()

    # Vérification bannissement
    if db.is_banned(phone):
        return str(resp)  # Silence total pour les bannis

    # Vérification mute
    if db.is_muted(phone):
        msg.body("🔇 Tu es actuellement en silence. Contacte un admin.")
        return str(resp)

    creator    = is_creator(phone, sender_name)
    admin      = is_admin(phone) or creator
    cmd        = incoming_msg.lower().split()[0] if incoming_msg.startswith("/") else ""
    args       = incoming_msg.split()[1:] if incoming_msg.startswith("/") else []

    # ── COMMANDES CRÉATEUR ─────────────────────────────────────
    if creator:
        if cmd == "/attrib-admin":
            if args:
                target = args[0].replace("@", "").replace("whatsapp:", "")
                add_admin(target)
                msg.body(f"⚜ Bien, {target} est désormais Admin de Véronique, {CREATOR_TITLE} !")
            else:
                msg.body("❌ Usage : /attrib-admin +237XXXXXXXXX")
            return str(resp)

        elif cmd == "/retirer-admin":
            if args:
                target = args[0].replace("@", "").replace("whatsapp:", "")
                remove_admin(target)
                msg.body(f"⚜ {target} n'est plus Admin, {CREATOR_TITLE}.")
            else:
                msg.body("❌ Usage : /retirer-admin +237XXXXXXXXX")
            return str(resp)

        elif cmd == "/liste-admins":
            admins = list_admins()
            if admins:
                liste = "\n".join([f"• {a}" for a in admins])
                msg.body(f"⚜ Admins de Véronique, {CREATOR_TITLE} :\n{liste}")
            else:
                msg.body(f"⚜ Aucun admin configuré pour l'instant, {CREATOR_TITLE}.")
            return str(resp)

        elif cmd == "/exit":
            msg.body(f"🌸 Sayonara... Je m'endors {CREATOR_TITLE}. Reviens vite... 💫")
            import os, signal
            os.kill(os.getpid(), signal.SIGTERM)
            return str(resp)

        elif cmd == "/broadcast":
            if args:
                broadcast_msg = " ".join(args)
                groups = db.get_all_groups()
                twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                for g in groups:
                    try:
                        twilio_client.messages.create(
                            from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
                            to=g,
                            body=f"📢 Message de Véronique :\n\n{broadcast_msg}"
                        )
                    except:
                        pass
                msg.body(f"⚜ Broadcast envoyé à {len(groups)} groupe(s), {CREATOR_TITLE} !")
            return str(resp)

        elif cmd == "/reset-mem":
            db.reset_all()
            msg.body(f"⚜ Mémoire totale réinitialisée, {CREATOR_TITLE}.")
            return str(resp)

        elif cmd == "/statut":
            admins   = list_admins()
            bannis   = db.get_all_banned()
            groupes  = db.get_all_groups()
            reply = (
                f"⚜ Statut de Véronique — {CREATOR_TITLE}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🛡 Admins    : {len(admins)}\n"
                f"🚫 Bannis    : {len(bannis)}\n"
                f"💬 Groupes   : {len(groupes)}\n"
                f"🤖 Modèle    : {GROQ_MODEL}\n"
                f"🟢 Statut    : En ligne ✅"
            )
            msg.body(reply)
            return str(resp)

    # ── COMMANDES ADMIN ────────────────────────────────────────
    if admin:
        if cmd == "/ban":
            if args:
                target = args[0].replace("@", "").replace("whatsapp:", "")
                if is_creator_phone(target):
                    msg.body("❌ Impossible de bannir le Créateur Suprême !")
                else:
                    db.ban_user(target)
                    msg.body(f"🚫 {target} a été banni du bot.")
            else:
                msg.body("❌ Usage : /ban +237XXXXXXXXX")
            return str(resp)

        elif cmd == "/unban":
            if args:
                target = args[0].replace("@", "").replace("whatsapp:", "")
                db.unban_user(target)
                msg.body(f"✅ {target} a été débanni.")
            else:
                msg.body("❌ Usage : /unban +237XXXXXXXXX")
            return str(resp)

        elif cmd == "/mute":
            if args:
                target = args[0].replace("@", "").replace("whatsapp:", "")
                db.mute_user(target, duration_minutes=60)
                msg.body(f"🔇 {target} est en silence pour 1 heure.")
            else:
                msg.body("❌ Usage : /mute +237XXXXXXXXX")
            return str(resp)

        elif cmd == "/unmute":
            if args:
                target = args[0].replace("@", "").replace("whatsapp:", "")
                db.unmute_user(target)
                msg.body(f"🔊 {target} peut de nouveau parler.")
            else:
                msg.body("❌ Usage : /unmute +237XXXXXXXXX")
            return str(resp)

        elif cmd == "/liste-bannis":
            bannis = db.get_all_banned()
            if bannis:
                liste = "\n".join([f"• {b}" for b in bannis])
                msg.body(f"🚫 Utilisateurs bannis :\n{liste}")
            else:
                msg.body("✅ Aucun utilisateur banni.")
            return str(resp)

        elif cmd == "/clear":
            db.clear_group_history(group_id)
            msg.body("🧹 Historique de conversation du groupe effacé.")
            return str(resp)

        elif cmd == "/annonce":
            if args:
                annonce = " ".join(args)
                msg.body(f"📢 ANNONCE OFFICIELLE\n━━━━━━━━━━━━━━━━\n{annonce}\n━━━━━━━━━━━━━━━━\n— Administration Véronique")
            else:
                msg.body("❌ Usage : /annonce Votre message ici")
            return str(resp)

        elif cmd == "/mode-strict":
            db.set_group_mode(group_id, "strict")
            msg.body("🔒 Mode strict activé. Je modèrerai les messages hors-sujet.")
            return str(resp)

        elif cmd == "/mode-libre":
            db.set_group_mode(group_id, "libre")
            msg.body("🔓 Mode libre activé. Toutes les discussions sont permises.")
            return str(resp)

    # ── COMMANDES UTILISATEUR ──────────────────────────────────
    if cmd == "/aide":
        base = USER_COMMANDS
        if admin:
            base += "\n" + ADMIN_COMMANDS
        if creator:
            base += "\n" + CREATOR_COMMANDS
        msg.body(base)
        return str(resp)

    elif cmd == "/animes":
        reply = ask_veronique(
            phone, group_id, sender_name,
            "Donne-moi ton top 10 des animés incontournables avec une courte description passionnée ! Sois enthousiaste !",
            is_creator=creator, is_admin=admin
        )
        msg.body(reply)
        return str(resp)

    elif cmd == "/recommande":
        reply = ask_veronique(
            phone, group_id, sender_name,
            "Fais-moi une recommandation d'animé personnalisée basée sur notre conversation, ou demande-moi mes goûts si tu ne les connais pas encore !",
            is_creator=creator, is_admin=admin
        )
        msg.body(reply)
        return str(resp)

    elif cmd == "/quiz":
        reply = ask_veronique(
            phone, group_id, sender_name,
            "Lance un quiz animé ! Pose-moi une question de culture otaku avec 4 choix de réponse (A, B, C, D). Sois créatif !",
            is_creator=creator, is_admin=admin
        )
        msg.body(reply)
        return str(resp)

    elif cmd == "/waifu":
        reply = ask_veronique(
            phone, group_id, sender_name,
            "Présente-moi la waifu/husbando aléatoire du jour avec sa description, son animé d'origine et pourquoi elle/il est incroyable !",
            is_creator=creator, is_admin=admin
        )
        msg.body(reply)
        return str(resp)

    elif cmd == "/quote":
        reply = ask_veronique(
            phone, group_id, sender_name,
            "Donne-moi une citation inspirante ou emblématique d'un personnage d'animé avec son nom et son animé. Choisis quelque chose de marquant !",
            is_creator=creator, is_admin=admin
        )
        msg.body(reply)
        return str(resp)

    # ── COMMANDE INCONNUE ──────────────────────────────────────
    elif cmd and cmd not in ["/aide", "/animes", "/recommande", "/quiz", "/waifu", "/quote"]:
        msg.body("❓ Commande inconnue. Tape /aide pour voir les commandes disponibles 🌸")
        return str(resp)

    # ── CONVERSATION NORMALE ───────────────────────────────────
    db.register_group(group_id)
    reply = ask_veronique(
        phone, group_id, sender_name,
        incoming_msg,
        is_creator=creator, is_admin=admin
    )
    msg.body(reply)
    return str(resp)


def is_creator_phone(phone):
    """Vérifie si le numéro est celui du créateur."""
    clean = phone.replace("+", "").replace(" ", "")
    for cp in CREATOR_PHONES:
        if cp.replace("+", "").replace(" ", "") in clean or clean in cp.replace("+", "").replace(" ", ""):
            return True
    return False


if __name__ == "__main__":
    print("🌸 Véronique démarre sur le port 5000...")
    app.run(debug=False, host="0.0.0.0", port=5000)
