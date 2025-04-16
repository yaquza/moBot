from telethon import TelegramClient
import asyncio
from telethon.tl.types import Channel, Chat
import signal
import sys
import time
import os

# === Telegram API Daten ===
api_id = 20139628
api_hash = '92849575cda87ffea1914f280252b316'

# === Konfigurationseinstellungen ===
WARTE_ZWISCHEN_NACHRICHTEN = 0.1  # Zeit in Sekunden zwischen einzelnen Nachrichten (schneller)
WARTE_NACH_X_NACHRICHTEN = 100     # Warten nach dieser Anzahl von Nachrichten
PAUSE_DAUER = 60                  # Wartezeit in Sekunden nach X Nachrichten (reduziert)
RUNDE_PAUSE = 1                   # Wartezeit in Sekunden nach einer kompletten Runde (reduziert)
SESSION_NAME = 'telegram_sender_session'

# === Dein Menütext ===
menü_text = """🅰️🅰️🅰️🅰️🅰️🅰️🅰️🅰️ ⭐️  
@HighCity3 – **Premium Trusted Vendor**  
**Diskret. Schnell. Sicher. International.**
💬 *Bestelle nur über geheimen Chat!*  
🔐 *Order via secret chat only!*
                    @HighCity3
                    @HighCity3
                    @HighCity3
                    @HighCity3
🚀✨✨✨✨💀
🔝 **High Quality Coke** 🔝  
➪ *Rolex Stamp* 👑 **90,6%**  
➪ *Fendi Stamp* 🥂 **91,9%**  
➪ *RS6 Stamp* 🏎️ **93,2%**
💰 50€ ~ 0.5g   150€ ~ 1.5g  
💰 100€ ~ 1.0g   250€ ~ 3.0g
— **PREMIUM COKE** —  
💎 60€ ~ 0.5g   180€ ~ 1.5g  
💎 120€ ~ 1.0g   270€ ~ 3.0g
• Shark Stamp **93,9%**  
• Dubai Diamond **94,2%**  
• Bottega Veneta **93,8%**  
🔸 *Bomben Qualität – top Feedback – blitzschnell geliefert!*
🍀✨✨✨✨🍀
**Weed Selections – 5g = 50€ | 25g = 200€ + 🎁**
**INDICA**  
- ZOMBIE VIRUS 🦠🧟‍♀️  
- BULL RIDER 🐮🤠  
- TIGER'S BLOOD 🐯🩸  
- BLACK MAMBA 🐍⚫️  
- DEATH STAR 🌟☠️  
**SATIVA**  
- LYON KING 🦁👑  
- SOUR JOKER 🍋🃏  
- PANAMA RED 🇵🇦🔴  
- POISON HAZE 🧪☠️  
- KING TUT ⚱️🫅  
- COSMIC ILLUSION 🪐🎆  
- MEXICAN SATIVA 🇲🇽⚡️  
**HYBRID**  
- RAINBOW CHEDDAR 🧀🌈  
- ITALIAN ICE 🇮🇹🍦  
- RICHIE RICH 🤘🏽🤑  
- DRAGON'S DREAM 🀄️🐲  
🔸 *Loud & fresh – perfekt getrimmt & kuratiert!*
✨✨✨✨  
**CRYSTALS & SPECIALS**  
• 1g – 40€  
• 2g – 70€  
🔸 *Glasklar, sauber, kein Misch – direkt Wirkung!*
• Kristallform – stark & rein!  
• Schnell, fein, zuverlässig!  
• Frische Paste – keine Streckung – sofort aktiv!  
• Bunte Teile – starker Turn – Party-Modus!
🎁 *Wöchentliche Deals | Treueboni | VIP-Angebote*  
✅ *Trusted & Verified – 100% safe delivery*  
**Kontakt:** @HighCity3  
🗝 *Nur über geheimen Chat bestellen!*
                    @HighCity3
                    @HighCity3
                    @HighCity3
                    @HighCity3"""

# === Globale Variable für Pausenzustand ===
ist_pausiert = False
start_zeit = None
gesamtstatistik = {"gesendet": 0, "fehler": 0, "runden": 0}

# === Funktion zum Behandeln von Tastatureingaben ===
def toggle_pause():
    global ist_pausiert
    ist_pausiert = not ist_pausiert
    status = "PAUSIERT" if ist_pausiert else "FORTGESETZT"
    print(f"\n[STEUERUNG] Programm {status}")
    return ist_pausiert

# === Signal-Handler für Strg+C ===
def signal_handler(sig, frame):
    print("\n\n=== PROGRAMM WIRD BEENDET ===")
    print(f"Gesamtstatistik:")
    print(f"- Gesendete Nachrichten: {gesamtstatistik['gesendet']}")
    print(f"- Fehlgeschlagene: {gesamtstatistik['fehler']}")
    print(f"- Vollständige Runden: {gesamtstatistik['runden']}")
    
    if start_zeit:
        laufzeit = time.time() - start_zeit
        stunden = int(laufzeit // 3600)
        minuten = int((laufzeit % 3600) // 60)
        sekunden = int(laufzeit % 60)
        print(f"- Laufzeit: {stunden}h {minuten}m {sekunden}s")
    
    print("Auf Wiedersehen!")
    sys.exit(0)

# === Funktion zur Zeitmessung ===
def zeit_formatieren(sekunden):
    h = int(sekunden // 3600)
    m = int((sekunden % 3600) // 60)
    s = int(sekunden % 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    elif m > 0:
        return f"{m}m {s}s"
    else:
        return f"{s}s"

# === Nachricht an alle Gruppen senden – Endlosschleife mit Logging & Pausen ===
async def sende_menü_endlos():
    global start_zeit, ist_pausiert, gesamtstatistik
    
    # Session erstellen und mit API verbinden
    async with TelegramClient(SESSION_NAME, api_id, api_hash) as client:
        print("\n=== TELEGRAM SENDER ===")
        print("Verbunden mit Telegram!")
        print("\nSTEUERUNG:")
        print("- Drücke STRG+C zum Beenden")
        print("- Drücke 'p' und Enter zum Pausieren/Fortsetzen")
        print("- Drücke 'i' und Enter für Statistik")
        print("- Drücke 's' und Enter zum Überspringen der aktuellen Gruppe")
        
        # Endlosschleife, damit das Skript kontinuierlich läuft
        start_zeit = time.time()
        überspringen = False
        
        while True:
            # Hole alle Dialoge (Chats, Gruppen, Kanäle)
            dialogs = await client.get_dialogs()
            
            # Filtere nur Gruppen
            gruppen = [
                dialog for dialog in dialogs
                if isinstance(dialog.entity, (Channel, Chat)) and dialog.is_group
            ]
            
            print(f"\n[INFO] Starte Runde {gesamtstatistik['runden'] + 1} – {len(gruppen)} Gruppen gefunden")
            
            # Zähler für erfolgreich gesendete Nachrichten und Fehler in dieser Runde
            gesendet_runde = 0
            fehler_runde = 0
            
            # Durchlaufe alle gefundenen Gruppen
            for i, gruppe in enumerate(gruppen, start=1):
                # Prüfe Tastatureingabe (nicht-blockierend)
                if sys.stdin in asyncio.get_event_loop()._ready:
                    cmd = sys.stdin.readline().strip().lower()
                    if cmd == 'p':
                        toggle_pause()
                    elif cmd == 'i':
                        print(f"\n[STATISTIK] Gesamt: {gesamtstatistik['gesendet']} gesendet, {gesamtstatistik['fehler']} Fehler")
                        print(f"Laufzeit: {zeit_formatieren(time.time() - start_zeit)}")
                    elif cmd == 's':
                        print(f"[STEUERUNG] Überspringe aktuelle Gruppe: {gruppe.name}")
                        überspringen = True
                
                # Prüfe Pausenzustand
                if ist_pausiert:
                    print("[PAUSE] Warte auf Fortsetzung... (Drücke 'p' und Enter zum Fortsetzen)")
                    while ist_pausiert:
                        await asyncio.sleep(1)
                        if sys.stdin in asyncio.get_event_loop()._ready:
                            cmd = sys.stdin.readline().strip().lower()
                            if cmd == 'p':
                                toggle_pause()
                
                # Wenn überspringen aktiviert ist, setze es zurück und fahre mit der nächsten Gruppe fort
                if überspringen:
                    überspringen = False
                    continue
                
                try:
                    # Sende den Menütext an die aktuelle Gruppe
                    await client.send_message(gruppe.entity, menü_text)
                    print(f"[{i}/{len(gruppen)}] ✅ Gesendet an: {gruppe.name}")
                    gesendet_runde += 1
                    gesamtstatistik['gesendet'] += 1
                    # Kurze Pause zwischen Nachrichten, um Rate-Limits zu vermeiden
                    await asyncio.sleep(WARTE_ZWISCHEN_NACHRICHTEN)
                except Exception as e:
                    # Fehlerbehandlung, falls eine Nachricht nicht gesendet werden kann
                    print(f"[{i}/{len(gruppen)}] ❌ Fehler bei {gruppe.name}: {str(e)[:50]}...")
                    fehler_runde += 1
                    gesamtstatistik['fehler'] += 1
                    await asyncio.sleep(WARTE_ZWISCHEN_NACHRICHTEN)
                    continue
                
                # Nach jeweils X gesendeten Nachrichten eine längere Pause einlegen
                if i % WARTE_NACH_X_NACHRICHTEN == 0 and i < len(gruppen):
                    restliche = len(gruppen) - i
                    print(f"[PAUSE] {PAUSE_DAUER} Sekunden Pause nach {WARTE_NACH_X_NACHRICHTEN} Nachrichten... (noch {restliche} Gruppen)")
                    
                    # Countdown für die Pause anzeigen
                    for sek in range(PAUSE_DAUER, 0, -1):
                        if ist_pausiert:
                            break
                        
                        # Prüfe auf Tastatureingabe während des Countdowns
                        if sys.stdin in asyncio.get_event_loop()._ready:
                            cmd = sys.stdin.readline().strip().lower()
                            if cmd == 'p':
                                toggle_pause()
                                break
                            elif cmd == 'i':
                                print(f"[STATISTIK] Aktuell: {gesendet_runde} gesendet, {fehler_runde} Fehler in dieser Runde")
                            elif cmd == 's':
                                print("[STEUERUNG] Pause übersprungen!")
                                break
                        
                        # Aktualisiere Countdown jede Sekunde
                        if sek % 5 == 0 or sek <= 5:
                            print(f"Weiter in {sek} Sekunden...", end="\r")
                        await asyncio.sleep(1)
                    
                    print(" " * 30, end="\r")  # Lösche die Countdown-Zeile
            
            # Statistik nach einem kompletten Durchlauf
            gesamtstatistik['runden'] += 1
            print(f"\n[RUNDE BEENDET] Erfolgreich: {gesendet_runde} | Fehler: {fehler_runde}")
            print(f"[GESAMT] Nachrichten: {gesamtstatistik['gesendet']} | Fehler: {gesamtstatistik['fehler']} | Runden: {gesamtstatistik['runden']}")
            
            laufzeit = time.time() - start_zeit
            print(f"Laufzeit: {zeit_formatieren(laufzeit)}")
            print(f"[INFO] Nächste Runde startet in {RUNDE_PAUSE} Sekunden...\n")
            
            # Countdown für die Pause zwischen Runden
            for sek in range(RUNDE_PAUSE, 0, -1):
                if ist_pausiert:
                    break
                
                # Prüfe auf Tastatureingabe während des Countdowns
                if sys.stdin in asyncio.get_event_loop()._ready:
                    cmd = sys.stdin.readline().strip().lower()
                    if cmd == 'p':
                        toggle_pause()
                        break
                
                if sek <= 3:
                    print(f"Neue Runde startet in {sek}...", end="\r")
                await asyncio.sleep(1)
            
            print(" " * 30, end="\r")  # Lösche die Countdown-Zeile

# === Start des Skripts ===
if __name__ == "__main__":
    # Registriere Signal-Handler für Strg+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Eingabe-Modus vorbereiten (nicht-blockierend)
    os.system('') if os.name == 'nt' else None  # Windows-Terminal-Fix
    
    print("Starte Telegram-Sender...")
    print("Verbinde mit Telegram...")
    
    try:
        # Starte die Endlosschleife
        asyncio.run(sende_menü_endlos())
    except KeyboardInterrupt:
        # Falls Strg+C gedrückt wird
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        print(f"Unerwarteter Fehler: {e}")
        sys.exit(1)