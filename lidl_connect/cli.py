#!/usr/bin/env python3
"""
Lidl Connect CLI
Kommandozeilen-Interface für das Toolkit
"""

import argparse
import sys
from lidl_connect.monitor import LidlConnectRefill


def main():
    parser = argparse.ArgumentParser(
        description="Lidl Connect Toolkit - Automatisierte Verwaltung"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Verfügbare Befehle")
    
    # Setup Befehl
    setup_parser = subparsers.add_parser("setup", help="Ersteinrichtung")
    
    # Monitor Befehl
    monitor_parser = subparsers.add_parser("monitor", help="Refill Monitor verwalten")
    monitor_parser.add_argument("action", choices=["start", "stop", "status", "logs"])
    
    args = parser.parse_args()
    
    if args.command == "setup":
        print("🦦 Lidl Connect Toolkit - Setup")
        print("Bitte folge der Anleitung in der README.md")
        
    elif args.command == "monitor":
        if args.action == "start":
            print("🚀 Starte Refill Monitor...")
            # TODO: Implementieren
        elif args.action == "stop":
            print("🛑 Stoppe Refill Monitor...")
            # TODO: Implementieren
        elif args.action == "status":
            print("📊 Prüfe Monitor Status...")
            # TODO: Implementieren
        elif args.action == "logs":
            print("📜 Zeige Logs...")
            # TODO: Implementieren
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
