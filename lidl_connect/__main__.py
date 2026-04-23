#!/usr/bin/env python3
"""
Lidl Connect Toolkit - Direkte Ausführung
"""

import asyncio
from lidl_connect.monitor import LidlConnectRefill

async def main():
    monitor = LidlConnectRefill()
    await monitor.run_monitor()

if __name__ == "__main__":
    asyncio.run(main())
