#!/usr/bin/env python3

#         Python Stream Deck Library
#      Released under the MIT license
#
#

# Example script showing some Stream Deck + specific functions

import os
import threading
import io

from PIL import Image
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices.StreamDeck import DialEventType, TouchscreenEventType

import subprocess



# =======================================
# Mute states for the apps on the dials
"""
dial_zero_mute = False
dial_zero_volume_memory = 0
dial_one_mute = False
dial_one_volume_memory = 0
dial_two_mute = False
dial_three_mute = False
"""
#
# =======================================


# Folder location of image assets used by this example.
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")

# image for idle state
img = Image.new('RGB', (120, 120), color='black')
released_icon = Image.open(os.path.join(ASSETS_PATH, 'Released.png')).resize((80, 80))
img.paste(released_icon, (20, 20), released_icon)

img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='JPEG')
img_released_bytes = img_byte_arr.getvalue()

# image for pressed state
img = Image.new('RGB', (120, 120), color='black')
pressed_icon = Image.open(os.path.join(ASSETS_PATH, 'Pressed.png')).resize((80, 80))
img.paste(pressed_icon, (20, 20), pressed_icon)

img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='JPEG')
img_pressed_bytes = img_byte_arr.getvalue()


# callback when buttons are pressed or released
def key_change_callback(deck, key, key_state):
    print("Key: " + str(key) + " state: " + str(key_state))

    deck.set_key_image(key, img_pressed_bytes if key_state else img_released_bytes)


# callback when dials are pressed or released
def dial_change_callback(deck, dial, event, value):
    if event == DialEventType.PUSH:
        print(f"dial pushed: {dial} state: {value}")

        if dial == 3 and value:
            deck.reset()
            deck.close()
        else:
            # build an image for the touch lcd
            img = Image.new('RGB', (800, 100), 'black')
            icon = Image.open(os.path.join(ASSETS_PATH, 'Exit.png')).resize((80, 80))
            img.paste(icon, (690, 10), icon)

            for k in range(0, deck.DIAL_COUNT - 1):
                img.paste(pressed_icon if (dial == k and value) else released_icon, (30 + (k * 220), 10),
                          pressed_icon if (dial == k and value) else released_icon)

            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            deck.set_touchscreen_image(img_byte_arr, 0, 0, 800, 100)
    elif event == DialEventType.TURN:
        print(f"dial {dial} turned: {value}")

        # change volume by +/-2% at a time
        if value < 0:
            value = -2
        else:
            value = 2

        # Firefox volume control
        if dial == 0:
            
            # run "wpctl status" and return its output
            wpctl_shell_out = subprocess.run(["wpctl", "status"], stdout=subprocess.PIPE)
            wpctl_string = wpctl_shell_out.stdout.decode("utf-8")

            # find the line with Firefox's stream id
            for line in wpctl_string.split("\n"):
                if "Firefox" in line and not "pid:" in line:
                    # remove whitespace before id and remove chars after id
                    id = line[8:].split(".")[0]
                    print(id)

                    wpctl_shell_out1 = subprocess.run(["wpctl", "get-volume", id], stdout=subprocess.PIPE)
                    firefox_volume = float(wpctl_shell_out1.stdout.decode("utf-8")[8:])*100
                    print(f"Current Firefox volume: {firefox_volume}")

                    firefox_volume = firefox_volume + float(value)
                    if firefox_volume > 100 or firefox_volume < 0:
                        print("you idiot")
                    else:
                        feedback = subprocess.run(["wpctl", "set-volume", id, f"{str(firefox_volume)}%"], stdout=subprocess.PIPE)
                        e = feedback.stdout.decode("utf-8")

                        print(e)

        # spotify volume control
        elif dial == 1:
            
            # run "wpctl status" and return its output
            wpctl_shell_out = subprocess.run(["wpctl", "status"], stdout=subprocess.PIPE)
            wpctl_string = wpctl_shell_out.stdout.decode("utf-8")

            # find the line with spotify's stream id
            for line in wpctl_string.split("\n"):
                if "spotify" in line and not "pid:" in line:
                    # remove whitespace before id and remove chars after id
                    id = line[8:].split(".")[0]
                    print(id)

                    wpctl_shell_out1 = subprocess.run(["wpctl", "get-volume", id], stdout=subprocess.PIPE)
                    spotify_volume = float(wpctl_shell_out1.stdout.decode("utf-8")[8:])*100
                    print(f"Current spotify volume: {spotify_volume}")

                    spotify_volume = spotify_volume + float(value)
                    if spotify_volume > 100 or spotify_volume < 0:
                        print("you idiot")
                    else:
                        feedback = subprocess.run(["wpctl", "set-volume", id, f"{str(spotify_volume)}%"], stdout=subprocess.PIPE)
                        e = feedback.stdout.decode("utf-8")

                        print(e)
        # minecraft volume control
        elif dial == 2:
            
            # run "wpctl status" and return its output
            wpctl_shell_out = subprocess.run(["wpctl", "status"], stdout=subprocess.PIPE)
            wpctl_string = wpctl_shell_out.stdout.decode("utf-8")
            print(wpctl_string)

            # find the line with minecraft's stream id
            for line in wpctl_string.split("\n"):
                if "java" in line and not "pid:" in line:
                    # remove whitespace before id and remove chars after id
                    id = line[8:].split(".")[0]
                    print(id)

                    wpctl_shell_out1 = subprocess.run(["wpctl", "get-volume", id], stdout=subprocess.PIPE)
                    minecraft_volume = float(wpctl_shell_out1.stdout.decode("utf-8")[8:])*100
                    print(f"Current minecraft volume: {minecraft_volume}")

                    minecraft_volume = minecraft_volume + float(value)
                    if minecraft_volume > 100 or minecraft_volume < 0:
                        print("you idiot")
                    else:
                        feedback = subprocess.run(["wpctl", "set-volume", id, f"{str(minecraft_volume)}%"], stdout=subprocess.PIPE)
                        e = feedback.stdout.decode("utf-8")

                        print(e)
            


# callback when lcd is touched
def touchscreen_event_callback(deck, evt_type, value):
    if evt_type == TouchscreenEventType.SHORT:
        print("Short touch @ " + str(value['x']) + "," + str(value['y']))

    elif evt_type == TouchscreenEventType.LONG:

        print("Long touch @ " + str(value['x']) + "," + str(value['y']))

    elif evt_type == TouchscreenEventType.DRAG:

        print("Drag started @ " + str(value['x']) + "," + str(value['y']) + " ended @ " + str(value['x_out']) + "," + str(value['y_out']))


if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()

    print("Found {} Stream Deck(s).\n".format(len(streamdecks)))

    for index, deck in enumerate(streamdecks):
        # This example only works with devices that have screens.

        if deck.DECK_TYPE != 'Stream Deck +':
            print(deck.DECK_TYPE)
            print("Sorry, this example only works with Stream Deck +")
            continue

        deck.open()
        deck.reset()

        deck.set_key_callback(key_change_callback)
        deck.set_dial_callback(dial_change_callback)
        deck.set_touchscreen_callback(touchscreen_event_callback)

        print("Opened '{}' device (serial number: '{}')".format(deck.deck_type(), deck.get_serial_number()))

        # Set initial screen brightness to 30%.
        deck.set_brightness(100)

        for key in range(0, deck.KEY_COUNT):
            deck.set_key_image(key, img_released_bytes)

        # build an image for the touch lcd
        img = Image.new('RGB', (800, 100), 'black')
        icon = Image.open(os.path.join(ASSETS_PATH, 'Exit.png')).resize((80, 80))
        img.paste(icon, (690, 10), icon)

        for dial in range(0, deck.DIAL_COUNT - 1):
            img.paste(released_icon, (30 + (dial * 220), 10), released_icon)

        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        touchscreen_image_bytes = img_bytes.getvalue()

        deck.set_touchscreen_image(touchscreen_image_bytes, 0, 0, 800, 100)

        # Wait until all application threads have terminated (for this example,
        # this is when all deck handles are closed).
        for t in threading.enumerate():
            try:
                t.join()
            except RuntimeError:
                pass