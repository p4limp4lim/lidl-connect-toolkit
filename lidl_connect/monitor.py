#!/usr/bin/env python3
"""
Lidl Connect Refill Monitor v2
Mit Session-Cookies und längeren Intervallen
"""

import asyncio
import re
import logging
import requests
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright
from lidl_connect.config import load_config

# Lade Konfiguration
CONFIG = load_config()
if not CONFIG:
    print("❌ Konfiguration fehlt! Siehe config.yaml.example")
    exit(1)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LidlConnectRefill:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.logged_in = False
    
    async def start(self):
        """Starte Browser mit gespeicherten Cookies"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=CONFIG["headless"])
        
        # Lade gespeicherte Cookies
        cookies = self.load_cookies()
        if cookies:
            self.context = await self.browser.new_context()
            await self.context.add_cookies(cookies)
            logger.info("Gespeicherte Cookies geladen")
        else:
            self.context = await self.browser.new_context()
        
        self.page = await self.context.new_page()
    
    def load_cookies(self):
        """Lade Cookies aus Datei"""
        try:
            if os.path.exists(CONFIG["cookie_file"]):
                with open(CONFIG["cookie_file"], 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Konnte Cookies nicht laden: {e}")
        return None
    
    def save_cookies(self):
        """Speichere Cookies in Datei"""
        try:
            cookies = asyncio.get_event_loop().run_until_complete(
                self.context.cookies()
            )
            with open(CONFIG["cookie_file"], 'w') as f:
                json.dump(cookies, f)
            logger.info("Cookies gespeichert")
        except Exception as e:
            logger.warning(f"Konnte Cookies nicht speichern: {e}")
    
    async def stop(self):
        """Beende Browser und speichere Cookies"""
        if self.context:
            try:
                cookies = await self.context.cookies()
                with open(CONFIG["cookie_file"], 'w') as f:
                    json.dump(cookies, f)
                logger.info("Cookies gespeichert")
            except Exception as e:
                logger.warning(f"Konnte Cookies nicht speichern: {e}")
        
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def check_login(self):
        """Prüfe ob noch eingeloggt"""
        try:
            await self.page.goto(CONFIG["url"], wait_until="networkidle")
            await asyncio.sleep(5)
            
            html = await self.page.content()
            
            # Prüfe ob Login-Formular noch da ist
            if 'input[name="msisdn"]' in html:
                logger.info("Nicht mehr eingeloggt - Login nötig")
                return False
            
            # Prüfe ob Dashboard geladen
            if 'Unlimited Refill' in html or 'Verbrauchsübersicht' in html:
                logger.info("Noch eingeloggt")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Fehler beim Login-Check: {e}")
            return False
    
    async def login(self):
        """Login bei Lidl Connect"""
        try:
            logger.info("Öffne Login-Seite...")
            await self.page.goto(CONFIG["url"], wait_until="networkidle")
            
            # Warte auf Login-Formular
            await self.page.wait_for_selector("input[name='msisdn']", timeout=10000)
            
            # Fülle Login-Daten ein
            await self.page.fill("input[name='msisdn']", CONFIG["username"])
            await self.page.fill("input[name='password']", CONFIG["password"])
            
            # Klicke Login
            await self.page.click("button[type='submit']")
            
            # Warte auf Dashboard
            await self.page.wait_for_load_state("networkidle")
            await asyncio.sleep(10)  # SPA-Rendering
            
            logger.info("Login erfolgreich!")
            return True
            
        except Exception as e:
            logger.error(f"Login fehlgeschlagen: {e}")
            return False
    
    async def get_refill_volume(self):
        """Hole das Refill-Volumen"""
        try:
            html = await self.page.content()
            
            # Pattern: "Unlimited Refill" gefolgt von HTML-Tags und dann Zahl + GB
            match = re.search(r'Unlimited\s+Refill.*?([\d,.]+)\s*\u003cspan', html, re.DOTALL)
            
            if match:
                available_str = match.group(1).replace(',', '.')
                available = float(available_str)
                
                logger.info(f"Refill-Volumen verfügbar: {available} GB")
                return available
            
            logger.warning("Konnte Refill-Volumen nicht finden")
            return None
            
        except Exception as e:
            logger.error(f"Fehler beim Auslesen: {e}")
            return None
    
    async def trigger_refill(self):
        """Triggere Nachbuchung"""
        try:
            logger.info("Versuche Nachbuchung...")
            
            # Klicke "Refill aktivieren"
            try:
                await self.page.click("text=Refill aktivieren", timeout=5000)
                logger.info("'Refill aktivieren' geklickt")
                await asyncio.sleep(3)
                return True
            except:
                logger.error("'Refill aktivieren' nicht gefunden")
                return False
            
        except Exception as e:
            logger.error(f"Fehler bei Nachbuchung: {e}")
            return False
    
    def send_notification(self, message):
        """Sende Telegram-Benachrichtigung"""
        try:
            url = f"https://api.telegram.org/bot{CONFIG['telegram_token']}/sendMessage"
            payload = {
                "chat_id": CONFIG["telegram_chat_id"],
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, data=payload, timeout=10)
            if response.status_code == 200:
                logger.info("Telegram-Benachrichtigung gesendet")
                return True
            else:
                logger.error(f"Fehler beim Senden: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Fehler beim Senden der Benachrichtigung: {e}")
            return False
    
    async def run_check(self):
        """Einzelne Prüfung mit Session-Wiederverwendung"""
        try:
            await self.start()
            
            # Prüfe ob noch eingeloggt
            if not await self.check_login():
                logger.info("Neuer Login nötig...")
                if not await self.login():
                    self.send_notification("❌ Lidl Connect: Login fehlgeschlagen!")
                    return False
            
            # Hole Refill-Volumen
            volume = await self.get_refill_volume()
            
            if volume is None:
                logger.error("Konnte Volumen nicht ermitteln")
                # Versuche nicht sofort zu benachrichtigen (könnte temporär sein)
                return False
            
            # Prüfe ob Nachbuchung nötig
            if volume < CONFIG["min_volume_gb"]:
                logger.warning(f"Refill-Volumen niedrig: {volume} GB!")
                self.send_notification(
                    f"⚠️ <b>Lidl Connect Refill</b>\n\n"
                    f"Refill-Volumen niedrig: <b>{volume} GB</b>\n"
                    f"Limit: {CONFIG['min_volume_gb']} GB\n\n"
                    f"Starte Nachbuchung..."
                )
                
                # Triggere Nachbuchung
                if await self.trigger_refill():
                    logger.info("Nachbuchung erfolgreich!")
                    self.send_notification(
                        f"✅ <b>Nachbuchung erfolgreich!</b>\n\n"
                        f"Neues Refill-Volumen verfügbar."
                    )
                else:
                    logger.error("Nachbuchung fehlgeschlagen!")
                    self.send_notification(
                        f"❌ <b>Nachbuchung fehlgeschlagen!</b>\n\n"
                        f"Bitte manuell nachbuchen."
                    )
            else:
                logger.info(f"Refill-Volumen OK: {volume} GB")
                # Nur bei niedrigem Volumen benachrichtigen (< 1 GB)
                if volume < 1.0:
                    self.send_notification(
                        f"ℹ️ <b>Lidl Connect Status</b>\n\n"
                        f"Refill-Volumen: <b>{volume} GB</b>\n"
                        f"Grenze: {CONFIG['min_volume_gb']} GB"
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Unerwarteter Fehler: {e}")
            return False
        finally:
            await self.stop()
    
    async def run_monitor(self):
        """Dauerhafte Überwachung"""
        logger.info(f"Lidl Connect Refill Monitor gestartet")
        logger.info(f"Prüfe alle {CONFIG['check_interval']} Sekunden")
        logger.info(f"Nachbuchen unter {CONFIG['min_volume_gb']} GB")
        
        # Erste Benachrichtigung
        self.send_notification(
            f"🦦 <b>Lidl Connect Monitor v2</b>\n\n"
            f"Monitor gestartet!\n"
            f"Prüfe alle {CONFIG['check_interval']//60} Minuten.\n"
            f"Cookies werden wiederverwendet."
        )
        
        while True:
            try:
                await self.run_check()
                logger.info(f"Warte {CONFIG['check_interval']} Sekunden...")
                await asyncio.sleep(CONFIG['check_interval'])
                
            except KeyboardInterrupt:
                logger.info("Monitor beendet")
                self.send_notification("🛑 Lidl Connect Monitor beendet")
                break
            except Exception as e:
                logger.error(f"Fehler in Hauptschleife: {e}")
                await asyncio.sleep(CONFIG['check_interval'])


async def main():
    """Hauptfunktion"""
    monitor = LidlConnectRefill()
    
    # Dauerüberwachung
    await monitor.run_monitor()


if __name__ == "__main__":
    asyncio.run(main())
