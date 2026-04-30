# 🛡️ Mini SOC — Détection & Blocage Brute Force SSH

> **Portfolio Cybersécurité** · Analyse de logs · Détection d'intrusion · Réponse automatisée

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-Server_22.04-E95420?style=flat-square&logo=ubuntu&logoColor=white)](https://ubuntu.com)
[![Kali](https://img.shields.io/badge/Kali-Linux-557C94?style=flat-square&logo=kalilinux&logoColor=white)](https://kali.org)
[![Status](https://img.shields.io/badge/Status-Terminé-brightgreen?style=flat-square)]()

---

## 📌 Présentation

Ce projet est une **simulation d'un mini Security Operations Center (SOC)** focalisé sur la détection et la réponse aux attaques brute force SSH.

Un script Python analyse en temps réel le fichier `/var/log/auth.log` d'un serveur Linux, identifie les IPs malveillantes dépassant un seuil de tentatives, déclenche une alerte et bloque automatiquement l'attaquant via `iptables`.

---

## ⚠️ Problème de sécurité adressé

Les serveurs exposés sur internet — en particulier via SSH — sont **constamment ciblés** par des attaques brute force automatisées.

Sans mesure de protection, les risques sont :

- Accès non autorisé au serveur
- Installation de malware ou backdoor
- Utilisation du serveur comme rebond pour attaquer d'autres systèmes
- Vol de données sensibles
- Déploiement de ransomware

---

## 🏗️ Architecture du lab

```
┌─────────────────────────┐         ┌─────────────────────────┐
│   VM 1 — Ubuntu Server  │◄────────│   VM 2 — Kali Linux     │
│   192.168.168.129       │  SSH    │   192.168.168.128       │
│                         │  :22    │                         │
│  • sshd actif           │         │  • Hydra (brute force)  │
│  • /var/log/auth.log    │         │  • rockyou.txt          │
│  • detect.py            │         │                         │
└─────────────────────────┘         └─────────────────────────┘
              Réseau NAT VMware — Les deux VMs se voient
```

**Rôles :**

| Machine | Rôle | Outils |
|---------|------|--------|
| Ubuntu Server `192.168.168.129` | Cible / Défense | sshd, iptables, Python |
| Kali Linux `192.168.168.128` | Attaquant simulé | Hydra, rockyou.txt |

---

## 📁 Structure du projet

```
01-mini-soc-ssh-bruteforce/
├── README.md
├── scripts/
│   └── detect.py           # Script de détection et blocage
└── screenshots/
    ├── 01-adduser.png
    ├── 02-ssh-status.png
    ├── 03-ssh-status.png
    ├── 04-ip-ubserver.png
    ├── 05-hydra-check.png
    ├── 06-ping-test.png
    ├── 07-world-list.png
    ├── 08-rock-you.png
    ├── 09-hydra-bforce.png
    ├── 10-auth-log-live.png
    ├── 11-pswd-find.png
    ├── 12-detection-script.png
    └── 13-hydra-blocked.png
```

---

## 🔬 Déroulement du projet

### Étape 1 — Création de l'utilisateur cible

Sur Ubuntu, création d'un compte utilisateur dédié avec un mot de passe volontairement faible, qui servira de cible pour l'attaque brute force.

```bash
sudo adduser cible
# mot de passe : Password123
```

> L'utilisateur `cible` est la victime simulée. Il ne dispose d'aucun privilège `sudo` — séparation des rôles avec le compte d'analyse `abdllxr`.

📸 `screenshots/01-adduser.png`

---

### Étape 2 — Vérification du service SSH

**Sans privilèges (compte `cible`) :**

```bash
systemctl status ssh
```

Le service SSH est actif, mais un warning apparaît indiquant que certains fichiers journaux ne sont pas accessibles — preuve que `cible` n'a pas les permissions super-utilisateur.

📸 `screenshots/02-ssh-status.png`

**Avec privilèges (compte `abdllxr`) :**

```bash
sudo systemctl status ssh
```

Le service SSH est actif (`running`), écoute sur toutes les interfaces réseau (`0.0.0.0`) au port 22. Cela confirme que la machine est accessible via SSH depuis n'importe quelle interface, ce qui constitue le prérequis pour le lab.

📸 `screenshots/03-ssh-status.png`

**Identification de l'adresse IP du serveur :**

```bash
ip a
```

L'adresse IP de la machine Ubuntu est `192.168.168.129` sur l'interface `ens33`. Cette adresse sera utilisée par Kali pour cibler le service SSH lors de l'attaque brute force.

📸 `screenshots/04-ip-ubserver.png`

---

### Étape 3 — Vérification de Hydra sur Kali

```bash
hydra -h
```

Hydra v9.6 est installé sur Kali Linux. Il sera utilisé pour automatiser les tentatives de connexion SSH sur le serveur Ubuntu au port 22.

📸 `screenshots/05-hydra-check.png`

---

### Étape 4 — Test de connectivité Kali → Ubuntu

```bash
ping -c 4 192.168.168.129
```

4 paquets envoyés, 4 reçus, 0% de perte. La machine Kali peut communiquer avec le serveur Ubuntu et est donc en mesure d'effectuer une attaque brute force sur son service SSH.

📸 `screenshots/06-ping-test.png`

---

### Étape 5 — Lancement de l'attaque brute force

**Préparation de la wordlist :**

```bash
ls /usr/share/wordlists/rockyou.txt.gz   # wordlist présente en version compressée
sudo gunzip rockyou.txt.gz               # décompression
ls -lh rockyou.txt                       # 134M — permissions : -rw-r--r--
```

Le propriétaire peut lire et modifier, le groupe et les autres peuvent uniquement lire.

📸 `screenshots/07-world-list.png` | `screenshots/08-rock-you.png`

**Lancement de l'attaque :**

```bash
hydra -l cible -P /usr/share/wordlists/rockyou.txt ssh://192.168.168.129 -t 4
```

- `-l cible` : utilisateur ciblé
- `-P rockyou.txt` : wordlist de mots de passe
- `-t 4` : 4 tâches parallèles maximum

> **Pourquoi `-t 4` ?** SSH limite nativement le nombre de connexions simultanées non authentifiées (`MaxStartups` dans `sshd_config`). Trop de threads parallèles déclencheraient des erreurs et rendraient l'attaque visible par un IDS/IPS.

📸 `screenshots/09-hydra-bforce.png`

---

### Observation des logs en temps réel (Ubuntu)

```bash
sudo tail -f /var/log/auth.log
```

L'attaque Hydra génère un pattern répétitif dans `auth.log` composé de 3 phases :

| Phase | Message | Signification |
|-------|---------|---------------|
| 1 | `Failed password for cible from 192.168.168.128` | Tentative échouée |
| 2 | `error: maximum authentication attempts exceeded` | Seuil SSH atteint |
| 3 | `Disconnecting authenticating user cible` | Session coupée par sshd, Hydra en ouvre une nouvelle |

Ce pattern répétitif révèle à l'analyste SOC qu'une attaque brute force est en cours sur le serveur.

📸 `screenshots/10-auth-log-live.png`

**Résultat de l'attaque :**

Après 201 tentatives, Hydra trouve le mot de passe : `Password123`.

```
[22][ssh] host: 192.168.168.129   login: cible   password: Password123
```

Le compte `cible` est compromis. L'attaquant dispose désormais d'un accès SSH valide au serveur, ce qui lui permet d'installer un backdoor, de voler des données, de déployer un ransomware ou d'utiliser le serveur comme rebond pour attaquer d'autres systèmes.

📸 `screenshots/11-pswd-find.png`

---

### Étape 6 — Détection et blocage automatique

Pour répondre à l'attaque, un script Python analyse `auth.log` et bloque automatiquement toute IP dépassant le seuil de 5 tentatives via `iptables`.

```bash
sudo python3 detect.py
```

**Résultat :**

```
-----tentative de brute force-----
[ALERT]: 192.168.168.128 -> 33 tentatives
[BLOCKED]: 192.168.168.128
```

L'IP `192.168.168.128` (Kali) est bloquée au niveau du pare-feu.

📸 `screenshots/12-detection-script.png`

**Impact côté attaquant (Kali) :**

```
[ERROR] all children were disabled due to too many connection errors
0 of 1 target completed, 0 valid password found
```

L'attaque est interrompue, Hydra est coupé, aucun mot de passe trouvé. Le blocage est efficace.

📸 `screenshots/13-hydra-blocked.png`

> **Note :** Dans ce lab, le script est lancé manuellement après l'attaque. Dans un environnement de production, il tournerait en continu en tâche de fond via un service `systemd` ou un `cron job`.

---

## 🐍 Script de détection (`detect.py`)

```python
import re
from collections import defaultdict
import subprocess

file_log = "/var/log/auth.log"

ip_pattern = r"\d+\.\d+\.\d+\.\d+"
ip_counts = defaultdict(int)

def block_ip(ip):
    subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])
    print(f"[BLOCKED]: {ip}")

def parse_log(file_log):
    with open(file_log, "r") as f:
        for line in f:
            if "Failed password" in line:
                match = re.search(ip_pattern, line)
                if match:
                    ip = match.group()
                    ip_counts[ip] += 1

    print("-----tentative de brute force-----")
    for ip, count in ip_counts.items():
        if count >= 5:
            print(f"[ALERT]: {ip} -> {count} tentatives")
            block_ip(ip)

parse_log(file_log)
```

---

## ✅ Ce que ce projet démontre

| Compétence | Détail |
|------------|--------|
| Analyse de logs | Lecture et parsing de `/var/log/auth.log` |
| Détection d'attaque | Identification du pattern brute force SSH |
| Scripting Python | Parsing regex, comptage, subprocess |
| Réponse aux incidents | Blocage IP automatique via iptables |
| Lab sécurité | Configuration de 2 VMs en réseau NAT |
| Documentation | Rapport technique structuré |

---

## 🔧 Améliorations possibles

- [ ] Exécution continue via `systemd` ou `cron`
- [ ] Notification par email lors d'une alerte
- [ ] Dashboard de visualisation des attaques
- [ ] Intégration avec un SIEM (Elastic, Splunk)
- [ ] Seuil et fenêtre temporelle configurables
- [ ] Export du rapport en JSON

---

## 👤 Auteur

**AbDouL** — Étudiant en licence de sécurité informatique (3ème année)
Objectif : Analyste Sécurité → Architecte Sécurité

🔗 [GitHub Portfolio](https://github.com/AbDouLB-D)