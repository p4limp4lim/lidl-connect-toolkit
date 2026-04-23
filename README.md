# 🦦 Lidl Connect Toolkit

Automatisierte Tools für Lidl Connect Vertragsmanagement.

## Features

- **Refill Monitor**: Überwacht das Datenvolumen und bucht automatisch nach
- **Session Management**: Cookies werden gespeichert und wiederverwendet
- **Telegram Notifications**: Benachrichtigungen bei niedrigem Volumen
- **Headless Browser**: Läuft im Hintergrund ohne GUI

## Installation

### Voraussetzungen

- Python 3.11+
- pip

### Schnellstart

```bash
# Repository klonen
git clone https://github.com/p4limp4lim/lidl-connect-toolkit.git
cd lidl-connect-toolkit

# Abhängigkeiten installieren
pip install -r requirements.txt

# Playwright Browser installieren
playwright install chromium
```

## Konfiguration

### Option 1: Config-Datei (empfohlen)

```bash
# Config-Verzeichnis erstellen
mkdir -p ~/.config/lidl-connect

# Beispiel-Config kopieren
cp config.yaml.example ~/.config/lidl-connect/config.yaml

# Config bearbeiten
nano ~/.config/lidl-connect/config.yaml
```

**config.yaml:**
```yaml
# Lidl Connect Zugangsdaten
username: "015123456789"  # Deine Lidl Connect Telefonnummer
password: "dein-passwort"  # Dein Lidl Connect Passwort

# Telegram Bot (für Benachrichtigungen)
# 1. Schreibe @BotFather auf Telegram und erstelle einen Bot
# 2. Kopiere den Token hier rein
telegram_token: "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"

# 3. Schreibe @userinfobot auf Telegram und hole deine Chat-ID
telegram_chat_id: "123456789"

# Einstellungen
min_volume_gb: 0.5        # Nachbuchen unter 500MB
check_interval: 300       # Prüfung alle 5 Minuten (Sekunden)
headless: true            # Browser unsichtbar im Hintergrund
```

### Option 2: Umgebungsvariablen

```bash
export LIDL_USERNAME="015123456789"
export LIDL_PASSWORD="dein-passwort"
export LIDL_TELEGRAM_TOKEN="123456789:ABC..."
export LIDL_TELEGRAM_CHAT_ID="123456789"
export LIDL_MIN_VOLUME="0.5"
export LIDL_CHECK_INTERVAL="300"
```

### Option 3: Docker

```bash
docker run -d \
  -e LIDL_USERNAME=015123456789 \
  -e LIDL_PASSWORD=dein-passwort \
  -e LIDL_TELEGRAM_TOKEN=123456789:ABC... \
  -e LIDL_TELEGRAM_CHAT_ID=123456789 \
  p4limp4lim/lidl-connect-toolkit
```

## Verwendung

### Monitor starten

```bash
# Direkt ausführen
python -m lidl_connect.monitor

# Oder als Service im Hintergrund
nohup python -m lidl_connect.monitor &
```

### Systemd Service

```bash
# Service-Datei erstellen
sudo cp lidl-connect.service /etc/systemd/system/

# Service aktivieren und starten
sudo systemctl enable lidl-connect
sudo systemctl start lidl-connect

# Status prüfen
sudo systemctl status lidl-connect

# Logs anzeigen
sudo journalctl -u lidl-connect -f
```

### Telegram Bot einrichten

1. **Bot erstellen:**
   - Schreibe @BotFather auf Telegram
   - Sende `/newbot`
   - Gib einen Namen ein (z.B. "Lidl Monitor")
   - Kopiere den Token

2. **Chat-ID herausfinden:**
   - Schreibe @userinfobot auf Telegram
   - Kopiere deine Chat-ID

3. **Testen:**
   ```bash
   curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
     -d "chat_id=<CHAT_ID>" \
     -d "text=🦦 Testnachricht!"
   ```

## Docker Compose

```yaml
version: '3.8'

services:
  lidl-connect:
    image: p4limp4lim/lidl-connect-toolkit
    container_name: lidl-connect
    restart: unless-stopped
    environment:
      - LIDL_USERNAME=015123456789
      - LIDL_PASSWORD=dein-passwort
      - LIDL_TELEGRAM_TOKEN=123456789:ABC...
      - LIDL_TELEGRAM_CHAT_ID=123456789
      - LIDL_MIN_VOLUME=0.5
      - LIDL_CHECK_INTERVAL=300
    volumes:
      - ./cookies:/tmp/lidl_connect_cookies.json
```

## Entwicklung

```bash
# Repository klonen
git clone https://github.com/p4limp4lim/lidl-connect-toolkit.git
cd lidl-connect-toolkit

# Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Playwright Browser installieren
playwright install chromium

# Tests ausführen
pytest
```

## Fehlerbehebung

### "Konnte Refill-Volumen nicht finden"

- Die Seite braucht länger zum Laden → Wartezeit erhöhen
- Lidl hat die Seite geändert → Regex anpassen
- Session abgelaufen → Cookies löschen und neu einloggen

### "Login fehlgeschlagen"

- Zugangsdaten prüfen
- Account nicht gesperrt?
- Rate-Limiting → Wartezeit erhöhen

### Browser-Probleme

```bash
# Playwright Browser neu installieren
playwright install --force chromium

# Browser-Cache löschen
rm -rf ~/.cache/ms-playwright
```

## Disclaimer

**🚨 WICHTIGER HINWEIS 🚨**

Dieses Tool ist **ausschließlich zu Testzwecken** gedacht und dient der **technischen Bildung**.

**Rechtliche Hinweise:**
- Die Nutzung dieses Tools kann gegen die **Nutzungsbedingungen von Lidl Connect** verstoßen
- Automatisierte Zugriffe auf die Lidl Connect Website können zur **Sperrung deines Kundenkontos** führen
- Lidl behält sich das Recht vor, Konten bei Verdacht auf Automatisierung zu **schließen oder zu sperren**

**Haftungsausschluss:**
- Die Nutzung erfolgt **ausschließlich auf eigenes Risiko**
- Der Autor übernimmt **keinerlei Haftung** für:
  - Gesperrte oder geschlossene Accounts
  - Verlorene Daten oder Guthaben
  - Rechtliche Konsequenzen
  - Sonstige Schäden

**Empfohlene Nutzung:**
- Nur zu **Test- und Bildungszwecken**
- Nicht zu häufig prüfen (empfohlen: alle 5 Minuten)
- Keine massiven automatisierten Aktionen
- Respektiere Rate-Limits
- Nutze das Tool **nicht produktiv** ohne Rücksprache mit Lidl

**Durch die Nutzung dieses Tools bestätigst du:**
- Dass du die Risiken verstehst
- Dass du die Verantwortung für dein Handeln trägst
- Dass der Autor nicht für Folgen haftet

---

**Verwendung auf eigene Gefahr!**

## Technische Details

- **Python 3.11+**
- **Playwright** für Browser-Automation
- **YAML** für Konfiguration
- **Requests** für HTTP-Requests

## Support

Bei Fragen oder Problemen:
- GitHub Issues
- GitHub: @p4limp4lim

---

**Made with 🦦**
