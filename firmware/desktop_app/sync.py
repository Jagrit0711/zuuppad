import time
import json
import os
import serial
import serial.tools.list_ports
import subprocess
import re

MACROPAD_DRIVE_PATH = None
SERIAL_PORT = None
ser = None

def find_macropad():
    global MACROPAD_DRIVE_PATH, SERIAL_PORT, ser
    ports = serial.tools.list_ports.comports()
    for port in ports:
        manufacturer = port.manufacturer or ""
        hwid = port.hwid or ""
        if "Adafruit" in manufacturer or "Raspberry Pi" in manufacturer or "Seeed" in manufacturer or "2E8A" in hwid or "2886" in hwid:
            SERIAL_PORT = port.device
            try:
                if not ser or not ser.is_open:
                    ser = serial.Serial(SERIAL_PORT, 115200, timeout=0.1)
                print(f"✅ Connected to Macropad on {SERIAL_PORT}")
            except Exception as e:
                if "Permission denied" in str(e):
                    print(f"\n⚠️ Permission denied on {SERIAL_PORT}. Requesting access via GUI...")
                    try:
                        subprocess.run(["pkexec", "chmod", "666", SERIAL_PORT], check=True)
                        print("✅ Permissions granted! Retrying connection...")
                        ser = serial.Serial(SERIAL_PORT, 115200, timeout=0.1)
                        print(f"✅ Connected to Macropad on {SERIAL_PORT}")
                    except Exception as pk_err:
                        print(f"❌ Failed to get permissions: {pk_err}")
                else:
                    print(f"Failed to connect to {SERIAL_PORT}: {e}")
            break

def get_media_info():
    title, artist, player_name = "", "", ""
    is_playing = False
    track_len, track_pos = 0, 0
    try:
        res = subprocess.run(["busctl", "--user", "list"], capture_output=True, text=True)
        players = [line.split()[0] for line in res.stdout.split('\n') if 'org.mpris.MediaPlayer2.' in line]
        
        for player in players:
            stat = subprocess.run(["busctl", "--user", "get-property", player, "/org/mpris/MediaPlayer2", "org.mpris.MediaPlayer2.Player", "PlaybackStatus"], capture_output=True, text=True)
            if '"Playing"' in stat.stdout:
                is_playing = True
                player_name = player.split(".")[-1].capitalize()
                
                meta = subprocess.run(["busctl", "--user", "get-property", player, "/org/mpris/MediaPlayer2", "org.mpris.MediaPlayer2.Player", "Metadata"], capture_output=True, text=True).stdout
                
                t_match = re.search(r'\"xesam:title\"\s+s\s+\"([^\"]+)\"', meta)
                if t_match: title = t_match.group(1)
                
                a_match = re.search(r'\"xesam:artist\"\s+as\s+1\s+\"([^\"]+)\"', meta)
                if a_match: artist = a_match.group(1)
                
                l_match = re.search(r'\"mpris:length\"\s+t\s+(\d+)', meta)
                if l_match: track_len = int(l_match.group(1)) // 1000000
                
                try:
                    pos_res = subprocess.run(["busctl", "--user", "get-property", player, "/org/mpris/MediaPlayer2", "org.mpris.MediaPlayer2.Player", "Position"], capture_output=True, text=True).stdout
                    p_match = re.search(r'x\s+(\d+)', pos_res)
                    if p_match: track_pos = int(p_match.group(1)) // 1000000
                except: pass
                break
    except: pass
    return is_playing, title, artist, player_name, track_pos, track_len

def get_lock_keys():
    caps, num = False, False
    try:
        if os.path.exists('/sys/class/leds/'):
            for d in os.listdir('/sys/class/leds/'):
                if 'capslock' in d.lower():
                    with open(f"/sys/class/leds/{d}/brightness", "r") as f:
                        if f.read().strip() == '1': caps = True
                if 'numlock' in d.lower():
                    with open(f"/sys/class/leds/{d}/brightness", "r") as f:
                        if f.read().strip() == '1': num = True
    except: pass
    return caps, num

import threading

# Global variables for async thread sharing
m_play, m_title, m_artist, m_player, m_pos, m_len = False, "", "", "", 0, 0

def media_fetcher_thread():
    global m_play, m_title, m_artist, m_player, m_pos, m_len
    while True:
        try:
            p, t, a, n, pos, l = get_media_info()
            m_play, m_title, m_artist, m_player, m_pos, m_len = p, t, a, n, pos, l
        except: pass
        time.sleep(0.1)

def sync_loop():
    global ser
    print("Zuup Sync Daemon Started. Running in background...")
    last_caps, last_num = get_lock_keys()
    
    # Start the async DBus fetcher
    threading.Thread(target=media_fetcher_thread, daemon=True).start()
    
    last_find_attempt = 0
    
    while True:
        try:
            if not ser or not ser.is_open:
                if time.time() - last_find_attempt > 5.0:
                    find_macropad()
                    last_find_attempt = time.time()
            
            if ser and ser.is_open:
                t = time.localtime()
                current_date = time.strftime("%b %d", t)
                current_day = time.strftime("%a", t)
                
                caps, num = get_lock_keys()
                
                caps_changed = caps != last_caps
                num_changed = num != last_num
                last_caps, last_num = caps, num
                
                payload = json.dumps({
                    "rtc": [t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec, t.tm_wday, t.tm_yday, t.tm_isdst],
                    "date": current_date,
                    "day": current_day,
                    "playing": m_play,
                    "title": m_title,
                    "artist": m_artist,
                    "player": m_player,
                    "caps": caps,
                    "num": num,
                    "caps_chg": caps_changed,
                    "num_chg": num_changed,
                    "pos": m_pos,
                    "len": m_len
                })
                
                ser.write((payload + "\r\n").encode())
        except Exception as e:
            ser = None # Reset serial connection on error so it attempts to reconnect
        time.sleep(0.1)

if __name__ == '__main__':
    sync_loop()
