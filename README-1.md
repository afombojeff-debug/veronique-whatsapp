# 🌸 VÉRONIQUE — Bot WhatsApp Otaku (Twilio + Groq)

Bot WhatsApp IA spécialisé animés, créé pour **Jeff Afombo Mbarga** — Créateur Suprême.

---

## 📁 Structure du projet

```
veronique_whatsapp/
├── app.py              → Serveur Flask + gestion des commandes
├── config.py           → Clés API + identité du créateur
├── auth.py             → Authentification créateur & admins
├── database.py         → Stockage JSON (bannis, historique, groupes)
├── veronique_ai.py     → Moteur IA Groq + personnalité
├── requirements.txt    → Dépendances Python
└── data/               → Créé automatiquement au démarrage
    ├── admins.json
    ├── banned.json
    ├── muted.json
    ├── groups.json
    ├── history.json
    └── modes.json
```

---

## ⚙️ Installation

```bash
pip install -r requirements.txt
```

---

## 🔑 Configuration (config.py)

```python
# Ton numéro WhatsApp (format international)
CREATOR_PHONES = ["+237690000000"]

# Clé Groq → https://console.groq.com (GRATUIT)
GROQ_API_KEY = "gsk_..."

# Twilio → https://console.twilio.com
TWILIO_ACCOUNT_SID     = "ACxxx..."
TWILIO_AUTH_TOKEN      = "xxx..."
TWILIO_WHATSAPP_NUMBER = "+14155238886"
```

---

## 🚀 Lancement

```bash
python app.py
```

Puis expose le port 5000 avec **ngrok** :
```bash
ngrok http 5000
```

Copie l'URL HTTPS dans le Webhook Twilio Sandbox :
`https://XXXX.ngrok.io/webhook`

---

## 💬 Commandes disponibles

### 👑 Créateur Suprême (Jeff Afombo Mbarga)
| Commande | Description |
|----------|-------------|
| `/attrib-admin +237XXX` | Donner le rôle admin à un numéro |
| `/retirer-admin +237XXX` | Retirer le rôle admin |
| `/liste-admins` | Voir tous les admins |
| `/broadcast <message>` | Envoyer un message à tous les groupes |
| `/reset-mem` | Réinitialiser toute la mémoire du bot |
| `/statut` | Voir le statut complet du bot |
| `/exit` | Éteindre Véronique |

### 🛡 Admins
| Commande | Description |
|----------|-------------|
| `/ban +237XXX` | Bannir un utilisateur |
| `/unban +237XXX` | Débannir un utilisateur |
| `/mute +237XXX` | Réduire au silence (1h) |
| `/unmute +237XXX` | Lever le silence |
| `/liste-bannis` | Voir les utilisateurs bannis |
| `/clear` | Effacer l'historique du groupe |
| `/annonce <message>` | Faire une annonce officielle |
| `/mode-strict` | Activer la modération stricte (animés only) |
| `/mode-libre` | Désactiver la modération stricte |

### 🌸 Tous les utilisateurs
| Commande | Description |
|----------|-------------|
| `/aide` | Afficher les commandes disponibles |
| `/animes` | Top 10 animés de Véronique |
| `/recommande` | Recommandation personnalisée |
| `/quiz` | Quiz animé surprise |
| `/waifu` | Waifu/Husbando du jour |
| `/quote` | Citation emblématique d'animé |

---

## 🏗 Déploiement en production

### Option 1 — Railway (recommandé, gratuit)
1. Push le code sur GitHub
2. Connecte Railway à ton repo
3. Ajoute les variables d'environnement
4. URL auto-générée → colle dans Twilio

### Option 2 — Render
1. Crée un Web Service sur render.com
2. Start command : `python app.py`
3. URL auto-générée → colle dans Twilio

---

## 🔒 Sécurité
- Jeff Afombo Mbarga est reconnu par **numéro ET nom d'affichage**
- Les admins sont stockés dans `data/admins.json`
- Impossible de bannir ou d'usurper l'identité du Créateur
- 3 tentatives max pour les commandes sensibles
