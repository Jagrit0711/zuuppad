import time
import board
import busio
import digitalio
import keypad
import json
import usb_hid
import supervisor
import random
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306
import rtc

macropad_rtc = rtc.RTC()

try:
    # ----------------- HARDWARE SETUP -----------------
    display = None
    try:
        displayio.release_displays()
        i2c = busio.I2C(scl=board.D5, sda=board.D4)
        try:
            import i2cdisplaybus
            display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
        except ImportError:
            display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
        display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32, rotation=180)
    except Exception as e:
        print("Display init failed:", e)

    # 2. Key Matrix
    row_pins = (board.D0, board.D1, board.D2)
    col_pins = (board.D3, board.D6, board.D7)
    matrix = keypad.KeyMatrix(row_pins, col_pins, columns_to_anodes=True)

    # 3. Rotary Encoder
    enc_a = digitalio.DigitalInOut(board.D8)
    enc_a.direction = digitalio.Direction.INPUT
    enc_a.pull = digitalio.Pull.UP
    enc_b = digitalio.DigitalInOut(board.D9)
    enc_b.direction = digitalio.Direction.INPUT
    enc_b.pull = digitalio.Pull.UP
    encoder_button = digitalio.DigitalInOut(board.D10)
    encoder_button.direction = digitalio.Direction.INPUT
    encoder_button.pull = digitalio.Pull.UP

    # ----------------- HID SETUP -----------------
    kbd = Keyboard(usb_hid.devices)
    layout = KeyboardLayoutUS(kbd)
    cc = ConsumerControl(usb_hid.devices)

    config = {"encoder": {"cw":"VOLUME_UP", "ccw":"VOLUME_DOWN", "press":"MUTE"}}

    # ----------------- UI SCREENS SETUP -----------------
    if display is not None:
        pal = displayio.Palette(2)
        pal[0] = 0x000000; pal[1] = 0xFFFFFF; pal.make_transparent(0)

        # 0. BOOT ANIMATION
        boot_group = displayio.Group()
        boot_lbl = label.Label(terminalio.FONT, text="ZUUP PAD", color=0xFFFFFF, scale=2, x=15, y=14)
        boot_group.append(boot_lbl)
        display.root_group = boot_group
        
        # Flashing Boot Animation
        for i in range(10):
            boot_lbl.hidden = not boot_lbl.hidden
            time.sleep(0.1)
        boot_lbl.hidden = False
        time.sleep(1)

        # 1. STANDBY SCREEN
        standby_group = displayio.Group()
        time_lbl = label.Label(terminalio.FONT, text="12:00", color=0xFFFFFF, scale=2, x=0, y=14)
        date_lbl = label.Label(terminalio.FONT, text="Jan 01", color=0xFFFFFF, x=65, y=8)
        day_lbl = label.Label(terminalio.FONT, text="Monday", color=0xFFFFFF, x=65, y=20)
        caps_lbl = label.Label(terminalio.FONT, text="[C]", color=0xFFFFFF, x=112, y=8)
        num_lbl = label.Label(terminalio.FONT, text="[N]", color=0xFFFFFF, x=112, y=20)
        caps_lbl.hidden = True
        num_lbl.hidden = True
        
        standby_group.append(time_lbl)
        standby_group.append(date_lbl)
        standby_group.append(day_lbl)
        standby_group.append(caps_lbl)
        standby_group.append(num_lbl)

        # 2. MEDIA SCREEN
        media_group = displayio.Group()
        song_lbl = label.Label(terminalio.FONT, text="Song Name", color=0xFFFFFF, x=35, y=8)
        media_group.append(song_lbl)
        
        # Visualizer Bars
        vis_bmp = displayio.Bitmap(25, 32, 2)
        vis_tg = displayio.TileGrid(vis_bmp, pixel_shader=pal, x=0, y=0)
        media_group.append(vis_tg)
        
        # Track progress bar (128x2) at the very bottom
        track_bmp = displayio.Bitmap(128, 2, 2)
        track_tg = displayio.TileGrid(track_bmp, pixel_shader=pal, x=0, y=30)
        media_group.append(track_tg)

        # 3. VOLUME SCREEN (Flicker-Free)
        vol_group = displayio.Group()
        vol_bmp = displayio.Bitmap(128, 32, 2)
        vol_tg = displayio.TileGrid(vol_bmp, pixel_shader=pal, x=0, y=0)
        vol_group.append(vol_tg)
        
        # Draw base speaker cone ONCE (flicker-free optimization)
        for x in range(35, 43):
            for y in range(12, 20): vol_bmp[x,y] = 1
        for i in range(8):
            for y in range(12 - i, 20 + i): vol_bmp[43 + i, y] = 1
            
        # 4. NOTIFICATION SCREEN (Lock Keys)
        notif_group = displayio.Group()
        notif_lbl = label.Label(terminalio.FONT, text="", color=0xFFFFFF, scale=2, x=5, y=14)
        notif_group.append(notif_lbl)

        # Initial screen
        display.root_group = standby_group

    # State variables
    last_enc_a = enc_a.value
    last_button_val = encoder_button.value
    
    target_volume = 50.0 
    current_volume = 50.0
    sys_muted = False
    
    is_playing = False
    track_pos = 0
    track_len = 0
    marquee_x = 35
    
    active_screen = "standby" # standby, media, volume, notif
    screen_timer = 0
    volume_sync_lock = 0
    last_tick = time.monotonic()
    serial_buffer = ""
    
    # Store last waves drawn so we only clear when needed
    last_waves_drawn = -1
    last_mute_drawn = False

    def set_screen(name):
        global active_screen
        if display is None or active_screen == name: return
        active_screen = name
        if name == "volume": display.root_group = vol_group
        elif name == "media": display.root_group = media_group
        elif name == "notif": display.root_group = notif_group
        else: display.root_group = standby_group

    def draw_visualizer():
        if display is None: return
        for x in range(25):
            for y in range(32): vis_bmp[x, y] = 0
        if is_playing and not sys_muted:
            for bar in range(5):
                h = random.randint(2, 28)
                bx = bar * 5
                for x in range(bx, bx+3):
                    for y in range(30-h, 30):
                        vis_bmp[x, y] = 1

    def draw_volume_waves():
        global last_waves_drawn, last_mute_drawn
        waves = max(0, min(3, int((current_volume / 100.0) * 4)))
        
        # Only redraw if state changed to avoid flicker
        if waves == last_waves_drawn and sys_muted == last_mute_drawn:
            return
            
        # Clear wave/mute area
        for x in range(55, 100):
            for y in range(0, 32): vol_bmp[x, y] = 0
            
        if sys_muted:
            # Draw X
            for i in range(8):
                vol_bmp[65 + i, 12 + i] = 1
                vol_bmp[65 + i, 20 - i] = 1
        else:
            # Draw waves
            for w in range(waves):
                dx = 60 + w * 6
                for y in range(12 - w*2, 20 + w*2): vol_bmp[dx, y] = 1
                
        last_waves_drawn = waves
        last_mute_drawn = sys_muted

    def show_notification(text):
        global screen_timer
        notif_lbl.text = text
        set_screen("notif")
        screen_timer = time.monotonic()

    print("Macropad initialized!")

    # ----------------- MAIN LOOP -----------------
    while True:
        now = time.monotonic()
        dt = now - last_tick
        last_tick = now
        
        # 1. Read Serial JSON (Metadata ONLY, Non-blocking)
        import sys
        if supervisor.runtime.serial_bytes_available:
            try:
                bytes_to_read = supervisor.runtime.serial_bytes_available
                serial_buffer += sys.stdin.read(bytes_to_read)
                if '\n' in serial_buffer:
                    lines = serial_buffer.split('\n')
                    serial_buffer = lines[-1]  # Keep remainder
                    line = lines[-2].strip()  # Process latest complete line
                    if line:
                        data = json.loads(line)
                        if "rtc" in data:
                            try: macropad_rtc.datetime = time.struct_time(tuple(data["rtc"]))
                            except: pass
                        
                        if display is not None:
                            if "caps" in data: caps_lbl.hidden = not data["caps"]
                            if "num" in data: num_lbl.hidden = not data["num"]
                            if "title" in data: song_lbl.text = data["title"]
                            if "playing" in data: is_playing = data["playing"]
                            if "pos" in data: track_pos = data["pos"]
                            if "len" in data: track_len = data["len"]
                            if "date" in data: date_lbl.text = data["date"]
                            if "day" in data: day_lbl.text = data["day"]
                            
                            if data.get("caps_chg"): show_notification("CAPS ON" if data["caps"] else "CAPS OFF")
                            if data.get("num_chg"): show_notification("NUM ON" if data["num"] else "NUM OFF")
            except Exception as e:
                pass

        # Independent RTC Time updates
        t = macropad_rtc.datetime
        time_lbl.text = "{:02}:{:02}".format(t.tm_hour, t.tm_min)
        
        # 2. Hardware Matrix Actions
        event = matrix.events.get()
        if event and event.pressed:
            idx = event.key_number
            if idx == 0: cc.send(ConsumerControlCode.SCAN_PREVIOUS_TRACK)
            elif idx == 1: cc.send(ConsumerControlCode.PLAY_PAUSE)
            elif idx == 2: cc.send(ConsumerControlCode.SCAN_NEXT_TRACK)
            elif idx == 3: kbd.send(Keycode.FOUR)
            elif idx == 4: kbd.send(Keycode.FIVE)
            elif idx == 5: kbd.send(Keycode.SIX)
            elif idx == 6: kbd.send(Keycode.SEVEN)
            elif idx == 7: kbd.send(Keycode.EIGHT)
            elif idx == 8: kbd.send(Keycode.NINE)

        # 3. Encoder (Doubled sensitivity by checking both rising and falling edges)
        curr_enc_a = enc_a.value
        if curr_enc_a != last_enc_a:
            set_screen("volume")
            screen_timer = now
            volume_sync_lock = now
            if enc_b.value == curr_enc_a: 
                cc.send(ConsumerControlCode.VOLUME_INCREMENT)
                target_volume = min(100.0, target_volume + 2.0)
            else:
                cc.send(ConsumerControlCode.VOLUME_DECREMENT)
                target_volume = max(0.0, target_volume - 2.0)
            last_enc_a = curr_enc_a

        # 4. Button (Mute Toggle)
        curr_btn = encoder_button.value
        if curr_btn == False and last_button_val == True:
            sys_muted = not sys_muted
            set_screen("volume")
            screen_timer = now
            cc.send(ConsumerControlCode.MUTE)
            time.sleep(0.05)
        last_button_val = curr_btn

        # 5. UI Updates & Animations
        if display is not None:
            if abs(current_volume - target_volume) > 0.5:
                current_volume += (target_volume - current_volume) * 0.3
            
            if active_screen == "volume":
                if now - screen_timer > 2.0:
                    set_screen("media" if is_playing else "standby")
                else:
                    draw_volume_waves()
                    
            elif active_screen == "notif":
                if now - screen_timer > 1.5:
                    set_screen("media" if is_playing else "standby")
            
            elif active_screen == "media":
                if not is_playing:
                    set_screen("standby")
                else:
                    marquee_x -= 1
                    if marquee_x < -200: marquee_x = 35
                    song_lbl.x = marquee_x
                    
                    if track_len > 0:
                        prog = int((track_pos / track_len) * 128)
                        for x in range(128):
                            c = 1 if x < prog else 0
                            track_bmp[x, 0] = c; track_bmp[x, 1] = c
                    else:
                        for x in range(128): track_bmp[x, 0] = 0; track_bmp[x, 1] = 0
                        
                    if int(now * 10) % 2 == 0:
                        draw_visualizer()
            
            elif active_screen == "standby":
                if is_playing:
                    set_screen("media")

        time.sleep(0.005)

except Exception as err:
    print("CRASHED:", err)
    if display is not None:
        err_group = displayio.Group()
        display.root_group = err_group
        err_group.append(label.Label(terminalio.FONT, text=str(err)[:20], color=0xFFFFFF, x=0, y=10))
    while True: time.sleep(1)
