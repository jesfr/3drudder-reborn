# 3dRudder Reborn — Journal de développement

## Objectif
Redonner vie au 3dRudder (périphérique foot controller, entreprise en faillite) sous forme d'un **exe unique sans installation** utilisable par des personnes non-techniques, notamment des personnes handicapées.

---

## Fonctionnalités implémentées

### Interface
- Interface moderne avec **CustomTkinter** (thème sombre)
- **Logo** affiché dans la fenêtre et dans la barre des tâches (logo.png / logo.ico)
- **Bascule FR / EN** en haut à droite (icône drapeau)
- Fenêtre redimensionnée automatiquement (500×780 normal, 500×1000 en mode clavier)

### Détection du périphérique
- Détection USB HID via **pygame** (pas de driver propriétaire requis)
- Indicateur de connexion en temps réel (point vert/rouge + texte)
- L'app attend le branchement sans crasher si le 3dRudder n'est pas connecté au lancement
- Reconnexion automatique si débranché/rebranché pendant l'utilisation

### Détection des pieds
- Indicateur "Pied détecté / non détecté" en temps réel
- Logique : si tous les axes = 0.0 → pied absent (méthode simple et fiable)

### Calibration
- Bouton "Étalonner" : capture la position actuelle comme point zéro
- Soustraction des offsets sur les 3 axes (roll, pitch, yaw)
- Retour visuel (bouton vert 2 secondes)

### Visualisation des axes
- 3 barres de progression en direct : Roll G/D, Pitch AV/AR, Yaw Rot
- Barres vertes quand actif, bleues quand inactif

### Mode souris
- Contrôle de la souris via les axes roll (X) et pitch (Y)
- Courbe exponentielle configurable (précision au centre)
- 3 sliders réglables : **Vitesse**, **Zone morte**, **Précision (exposant)**

### Mode clavier
- Mappage personnalisable de 6 touches : Avant, Arrière, Droite, Gauche, Rot. droite, Rot. gauche
- Panneau de configuration dépliable dans l'interface
- Bouton "Appliquer" pour valider le mapping
- Axe pitch corrigé (avant/arrière dans le bon sens)

### Mode manette (Xbox virtuelle)
- Contrôle via **vgamepad** (Xbox 360 virtuelle via ViGEmBus)
- Joystick gauche = roll/pitch, joystick droit = yaw
- Détection de ViGEmBus via le **registre Windows** (fiable, sans tentative d'instanciation)
- Si ViGEmBus absent : fenêtre d'installation avec le **MSI embarqué** dans l'exe (pas d'internet requis)
- `ViGEmClient.dll` embarquée via `--add-binary` pour résoudre les dépendances

### Firmware
- Affichage de la version firmware détectée sur le périphérique
- Bouton "Flash Firmware" avec avertissement clair
- Installateur `FwInstaller2_PC_NS_1442.exe` embarqué dans l'exe

### Feedback
- Formulaire de feedback intégré (nom, message, calcul anti-bot)
- Envoi par **SMTP Gmail** vers adresse personnelle
- Identifiants **XOR-obfusqués** dans le code (invisibles dans le binaire et sur GitHub)

### Don PayPal
- Bouton "Don PayPal" ouvrant le lien dans le navigateur

### Persistance des réglages
- Sauvegarde automatique dans `settings.json` à côté de l'exe
- Paramètres sauvegardés : langue, vitesse, zone morte, précision, mapping clavier
- Chargement au démarrage, sauvegarde à chaque changement de slider, à l'application du mapping, au changement de langue, et à la fermeture de la fenêtre

---

## Distribution

### Build PyInstaller
```
python -m PyInstaller --onefile --windowed --icon=logo.ico
  --add-data "logo.png;."
  --add-data "logo.ico;."
  --add-data "3DR Bootstrap Kit/FwInstaller2_PC_NS_1442.exe;3DR Bootstrap Kit"
  --add-data "vgamepad/.../ViGEmBusSetup_x64.msi;vgamepad/win/vigem/install/x64"
  --add-data "vgamepad/.../ViGEmBusSetup_x86.msi;vgamepad/win/vigem/install/x86"
  --add-binary "vgamepad/.../ViGEmClient.dll;vgamepad/win/vigem/client/x64"
  --add-binary "vgamepad/.../ViGEmClient.dll;vgamepad/win/vigem/client/x86"
  --name "3dRudder_Reborn" app.py
```

### Résultat
- `dist/3dRudder_Reborn.exe` — fichier unique, sans installation
- `settings.json` créé automatiquement à côté de l'exe au premier usage

---

## Bugs corrigés

| Problème | Cause | Fix |
|---|---|---|
| Axes figés après refactor | `pygame.joystick.quit()/init()` invalidait la référence | Supprimé, pygame 2.x gère seul |
| Statut toujours "Connecté" | `get_axis()` ne lève pas d'exception à la déconnexion | `find_3drudder()` à chaque poll |
| App crash sans 3dRudder | `exit(1)` au démarrage | `joy=None` passé à App, UI désactivée |
| VGAMEPAD_OK toujours True | Import seul ne teste pas le driver | Vérification registre Windows |
| Bouton Activer sans retour visuel | Code de mise à jour bouton mal placé après refactor | Replacé dans `_activate()` |
| DLL vgamepad non chargée dans l'exe | `--add-data` ne résout pas les dépendances DLL | Remplacé par `--add-binary` |
| Avant/Arrière inversés en mode clavier | Axe pitch positif vers l'arrière | `-pitch` dans le mapping |
| URL ViGEmBus morte (404) | Lien GitHub hardcodé vers ancienne version | MSI embarqué dans l'exe |
| Dialogue "déjà installé" au clic installer | Détection via `VX360Gamepad()` échouait même si installé | Détection via registre |

---

## Fichiers du projet

| Fichier | Rôle |
|---|---|
| `app.py` | Code source principal |
| `logo.png` | Logo affiché dans l'app |
| `logo.ico` | Icône barre des tâches / exe |
| `settings.json` | Réglages utilisateur (créé au premier lancement) |
| `3DR Bootstrap Kit/FwInstaller2_PC_NS_1442.exe` | Installateur firmware embarqué |
| `read_axes.py` | Script de test axes (référence) |
| `dist/3dRudder_Reborn.exe` | Exe distributable final |
