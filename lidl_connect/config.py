#!/usr/bin/env python3
"""
Konfigurations-Loader für Lidl Connect Toolkit
"""

import os
import yaml
from pathlib import Path


def load_config():
    """Lade Konfiguration aus Datei oder Umgebungsvariablen"""
    
    # Standard-Config
    config = {
        "username": "",
        "password": "",
        "url": "https://kundenkonto.lidl-connect.de/mein-lidl-connect.html",
        "headless": True,
        "min_volume_gb": 0.5,
        "check_interval": 300,
        "telegram_token": "",
        "telegram_chat_id": "",
        "cookie_file": "/tmp/lidl_connect_cookies.json"
    }
    
    # Versuche Config-Datei zu laden
    config_paths = []
    
    # Prüfe Umgebungsvariable
    if 'LIDL_CONFIG' in os.environ:
        config_paths.append(os.environ['LIDL_CONFIG'])
    
    # Standard-Pfade
    config_paths.extend([
        os.path.expanduser("~/.config/lidl-connect/config.yaml"),
        os.path.expanduser("~/.lidl-connect/config.yaml"),
        "/etc/lidl-connect/config.yaml",
        "config.yaml",  # Aktuelles Verzeichnis
    ])
    
    for path in config_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    file_config = yaml.safe_load(f)
                    if file_config:
                        config.update(file_config)
                        print(f"✅ Config geladen aus: {path}")
                        break
            except Exception as e:
                print(f"⚠️ Fehler beim Laden von {path}: {e}")
    
    # Umgebungsvariablen überschreiben Config-Datei
    env_mapping = {
        "LIDL_USERNAME": "username",
        "LIDL_PASSWORD": "password",
        "LIDL_TELEGRAM_TOKEN": "telegram_token",
        "LIDL_TELEGRAM_CHAT_ID": "telegram_chat_id",
        "LIDL_MIN_VOLUME": "min_volume_gb",
        "LIDL_CHECK_INTERVAL": "check_interval",
    }
    
    for env_var, config_key in env_mapping.items():
        if env_var in os.environ:
            # Konvertiere Typen
            if config_key in ["min_volume_gb"]:
                config[config_key] = float(os.environ[env_var])
            elif config_key in ["check_interval"]:
                config[config_key] = int(os.environ[env_var])
            elif config_key in ["headless"]:
                config[config_key] = os.environ[env_var].lower() in ["true", "1", "yes"]
            else:
                config[config_key] = os.environ[env_var]
    
    # Validiere erforderliche Felder
    required = ["username", "password", "telegram_token", "telegram_chat_id"]
    missing = [field for field in required if not config.get(field)]
    
    if missing:
        print(f"❌ Fehlende Konfiguration: {', '.join(missing)}")
        print("Bitte erstelle eine config.yaml oder setze Umgebungsvariablen")
        print("Siehe config.yaml.example für Details")
        return None
    
    return config


if __name__ == "__main__":
    # Test
    config = load_config()
    if config:
        print(f"\n✅ Konfiguration geladen:")
        print(f"   Username: {config['username']}")
        print(f"   Telegram: {config['telegram_chat_id']}")
        print(f"   Intervall: {config['check_interval']}s")
    else:
        print("\n❌ Konfiguration unvollständig!")
