# 🔐 Projet Flask + Vault + MariaDB — Authentification sécurisée avec TOTP et Anti-rejeu

Ce projet met en place une **authentification complète et sécurisée** pour une application Flask, avec intégration de :

✅ Base de données **MariaDB** initialisée automatiquement  
✅ Stockage des secrets dans **HashiCorp Vault**  
✅ Authentification **avec mot de passe + TOTP** (Google Authenticator compatible)  
✅ Protection **anti-rejeu des codes TOTP**  
✅ Communication sécurisée entre services via Docker Compose

---

## 📁 Structure du projet

| Fichier / Dossier    | Rôle                                                              |
| -------------------- | ----------------------------------------------------------------- |
| `app.py`             | Application Flask avec routes login, TOTP, et accès sécurisé      |
| `init.sql`           | Initialise la base de données avec des utilisateurs et des livres |
| `Dockerfile`         | Image Python qui attend MariaDB avant de démarrer Flask           |
| `init-vault.sh`      | Initialise Vault avec les secrets de connexion                    |
| `docker-compose.yml` | Déploie tous les services (MariaDB, Vault, Flask)                 |
| `requirements.txt`   | Dépendances Python (`flask`, `pyotp`, `hvac`, etc.)               |

---

## 🚀 Lancement rapide

### 1. Démarrer les services

```bash
docker-compose down -v
docker-compose up --build
```

Cela démarre :

- `mariadb` (base avec utilisateurs/livres)
- `vault` (stocke les secrets d’accès)
- `app` (application Flask avec sécurité)

---

## 🔐 Authentification en 2 étapes (mot de passe + TOTP)

### Identifiants par défaut

- **Utilisateur** : `admin`
- **Mot de passe** : `adminpass`
- **Secret TOTP** : `JBSWY3DPEHPK3PXP` (à scanner dans Google Authenticator)

### Générer un code TOTP à la main (si besoin)

```python
import pyotp
print(pyotp.TOTP("JBSWY3DPEHPK3PXP").now())
```

---

## 🛡️ Sécurité intégrée

### 🔸 1. Authentification classique (étape 1)

- Le mot de passe est hashé en SHA-256 côté serveur
- Vérification contre la valeur en base (`users.password`)
- Si le mot de passe est correct → redirection vers `/2fa`

### 🔸 2. Authentification TOTP (étape 2)

- Le serveur utilise `pyotp` pour générer et vérifier le code TOTP à 6 chiffres
- La clé secrète est propre à chaque utilisateur (`users.totp_secret`)
- Compatible avec Google Authenticator, FreeOTP…

### 🔸 3. Anti-rejeu TOTP (protection avancée)

- Chaque code TOTP utilisé est enregistré dans la table `used_totp`
- Si un utilisateur tente de réutiliser le **même code dans la même fenêtre de 30 secondes**, il est **rejeté** (`403`)
- Nettoyage automatique des anciens codes (TTL configurable)

Extrait SQL :

```sql
CREATE TABLE used_totp (
  username VARCHAR(255),
  code VARCHAR(6),
  used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (username, code)
);
```

---

## 🔎 Tester la sécurité manuellement

### 🔁 Test de rejeu TOTP

1. Connectez-vous avec `admin` / `adminpass` + code TOTP
2. Déconnectez-vous (ou navigation privée)
3. Reconnectez-vous avec **le même code** (encore valide 30s)  
   ➜ 🔥 **Résultat attendu** : `Code TOTP déjà utilisé`
4. Attendez 30s, utilisez un **nouveau code TOTP**  
   ➜ ✅ Connexion acceptée

---

## ✅ Fonctionnalités implémentées

- [x] Authentification sécurisée via mot de passe
- [x] Validation TOTP (2FA)
- [x] Système **anti-rejeu** des codes TOTP
- [x] Lecture sécurisée des secrets Vault
- [x] Base de données initialisée automatiquement
- [x] Déploiement complet avec Docker Compose

---

## 📌 Améliorations possibles

- Génération automatique de QR Code à l’inscription
- Expiration automatique des anciens codes TOTP (`DELETE FROM used_totp WHERE used_at < NOW() - INTERVAL 2 MINUTE`)
- Intégration HTTPS + JWT
- Front-end CSS / Bootstrap

---

## 📷 Aperçu

```
➤ Page de login : /login
➤ Étape TOTP : /2fa
➤ Page principale : / (liste des livres)
```

---
