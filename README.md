# 🤖 Pwnagotchi Analyzer

Interface web dockerisée pour analyser les captures WiFi de votre Pwnagotchi de manière éthique et sécurisée.

## ⚠️ DISCLAIMER IMPORTANT

**CET OUTIL EST DESTINÉ UNIQUEMENT À UN USAGE ÉTHIQUE ET LÉGAL :**
- ✅ Testez uniquement vos propres réseaux WiFi
- ✅ Utilisez avec autorisation explicite écrite
- ✅ Respectez les lois locales sur la cybersécurité
- ❌ Ne pas utiliser sur des réseaux tiers sans permission
- ❌ Ne pas utiliser pour des activités malveillantes

## 🚀 Fonctionnalités

### Interface Web Intuitive
- 📁 Upload de fichiers PCAP/CAP
- 🎯 Sélection de dictionnaires de mots de passe
- 📊 Suivi en temps réel des analyses
- 📈 Historique et statistiques

### Outils Intégrés
- **Hashcat** - Crackage GPU/CPU optimisé
- **Aircrack-ng** - Analyse classique
- **HCXtools** - Conversion de formats
- **John the Ripper** - Attaques avancées

### Dictionnaires Inclus
- **RockYou** (14M mots de passe)
- **Top 10M** (mots de passe courants)
- **SecLists** (patterns spécialisés)
- **Dictionnaires français** (localisés)

## 🐳 Installation avec Docker

### Prérequis
```bash
# Docker et Docker Compose
sudo apt install docker.io docker-compose

# Permissions utilisateur (optionnel)
sudo usermod -aG docker $USER
```

### Démarrage rapide
```bash
# Cloner le projet
git clone https://github.com/votre-repo/pwnagotchi-analyzer
cd pwnagotchi-analyzer

# Construire et démarrer
docker-compose up --build

# Interface disponible sur:
# http://localhost:8888
```

## 📁 Structure du Projet

```
pwnagotchi-analyzer/
├── docker-compose.yml      # Configuration Docker
├── Dockerfile             # Image personnalisée
├── requirements.txt       # Dépendances Python
├── app.py                # Application Flask
├── templates/            # Interface web
│   ├── index.html
│   ├── task_status.html
│   └── tasks.html
├── captures/            # Fichiers PCAP uploadés
├── results/            # Résultats d'analyse
├── wordlists/         # Dictionnaires
└── logs/             # Logs d'utilisation
```

## 🔧 Utilisation

### 1. Récupérer les captures de votre Pwnagotchi
```bash
# Via SSH
scp [user]@[nom_raspberry].local:/root/handshakes/*.pcap ./captures/

# Ou via l'interface web du Pwnagotchi
# http://[nom_raspberry].local:8080
```

### 2. Analyser via l'interface web
1. Accédez à `http://localhost:8888`
2. Uploadez votre fichier `.pcap`
3. Sélectionnez un dictionnaire
4. Lancez l'analyse
5. Suivez le progrès en temps réel

### 3. Consultation des résultats
- Interface web : Résultats affichés directement
- Fichiers : Disponibles dans `/results/`
- API : Endpoints JSON pour intégration

## 🛡️ Sécurité

### Isolation Docker
- Environnement containerisé
- Accès réseau limité
- Stockage des données isolé

### Logging et Audit
- Toutes les analyses sont loggées
- Horodatage des activités
- Traçabilité complète

### Bonnes Pratiques
- Changez les mots de passe par défaut
- Utilisez HTTPS en production
- Sauvegardez régulièrement vos données
- Respectez les réglementations locales

## 📊 Exemples d'Analyse

### Test de robustesse de votre réseau
```bash
# Exemple de résultat
Network: MonWiFi_5G
BSSID: AA:BB:CC:DD:EE:FF
Password: motdepasse123
Time: 45 seconds
Status: ⚠️ FAIBLE - Changez votre mot de passe !
```

### Recommandations automatiques
- Mots de passe < 8 caractères → **Critique**
- Mots de passe courants → **Élevé**
- Mots de passe complexes → **Sécurisé**

## 🔄 Workflow Typique

1. **Capture** avec Pwnagotchi (mode auto)
2. **Récupération** des fichiers .pcap
3. **Upload** dans l'analyzer
4. **Analyse** avec dictionnaires appropriés
5. **Évaluation** de la sécurité
6. **Amélioration** des mots de passe si nécessaire

## 🎓 Aspects Éducatifs

### Apprentissage de la Sécurité
- Comprendre les protocoles WPA/WPA2
- Importance des mots de passe forts
- Techniques d'attaque par dictionnaire
- Méthodologies de test de pénétration

### Sensibilisation
- Démonstration pratique des vulnérabilités
- Impact du choix des mots de passe
- Évolution des standards de sécurité

## 🚨 Responsabilité Légale

**L'utilisateur est entièrement responsable de l'usage de cet outil.**

- Respectez les lois sur la cybersécurité
- Obtenez toujours les autorisations nécessaires
- N'utilisez que sur vos propres systèmes
- Documentez vos activités de test

## 🤝 Contribution

Les contributions sont bienvenues ! Merci de :
- Suivre les guidelines éthiques
- Respecter les standards de sécurité
- Documenter vos modifications
- Tester avant de soumettre

**Utilisez de manière responsable et éthique ! 🛡️**