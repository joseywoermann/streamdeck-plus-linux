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

# TODO: move this to a config.json
program_zero = {
    "name": "Spotify",
    "id": "spotify"
}

programOne = {
    "name": "Feishin",
    "id": "Chromium"
}

programTwo = {
    "name": "Minecraft",
    "id": "java"
}

programThree = {
    "name": "N/A",
    "id": "n/a"
}

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


"""
# don't need this for now
# callback when buttons are pressed or released
def key_change_callback(deck, key, key_state):
    print("Key: " + str(key) + " state: " + str(key_state))

    deck.set_key_image(key, img_pressed_bytes if key_state else img_released_bytes)
"""

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
        #print(f"dial {dial} turned: {value}")

        # change volume by +/-2% at a time
        if value < 0:
            value = -2
        else:
            value = 2


        # Volume control program zero
        # TODO: break this out into a function that takes to dial number as a parameter and adjusts the volume of the corresponding program according to the dict above
        if dial == 0:
            
            # run "wpctl status" and return its output
            wpctl_shell_out = subprocess.run(["wpctl", "status"], stdout=subprocess.PIPE)
            wpctl_string = wpctl_shell_out.stdout.decode("utf-8")

            # find the line with the program's id
            for line in wpctl_string.split("\n"):
                if program_zero["id"] in line and not "pid:" in line:

                    # extract the digits from the line
                    shell_list = list(line)
                    for i in shell_list:
                        if i == " ":
                            shell_list.remove(i)
                    node_id = "".join(shell_list).split(".")[0]

                    # get current app volume
                    wpctl_shell_out1 = subprocess.run(["wpctl", "get-volume", node_id], stdout=subprocess.PIPE)
                    p_z_volume = float(wpctl_shell_out1.stdout.decode("utf-8")[8:])*100
                    
                    if p_z_volume + float(value) > 100: 
                        print("Cannot set volume to higher than 100.")
                    elif p_z_volume + float(value) < 0:
                        print("Cannot set volume to below 0.")
                    else:
                        p_z_volume = p_z_volume + float(value)
                        subprocess.run(["wpctl", "set-volume", node_id, f"{str(p_z_volume)}%"], stdout=subprocess.PIPE)
                        print(f"Set {program_zero["name"]} volume to {p_z_volume}. [Pipewire Node ID: {node_id}]")


        
            

"""
# don't need this for now
# callback when lcd is touched
def touchscreen_event_callback(deck, evt_type, value):
    if evt_type == TouchscreenEventType.SHORT:
        print("Short touch @ " + str(value['x']) + "," + str(value['y']))

    elif evt_type == TouchscreenEventType.LONG:

        print("Long touch @ " + str(value['x']) + "," + str(value['y']))

    elif evt_type == TouchscreenEventType.DRAG:

        print("Drag started @ " + str(value['x']) + "," + str(value['y']) + " ended @ " + str(value['x_out']) + "," + str(value['y_out']))
"""

if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()

    print("Found {} Stream Deck(s).\n".format(len(streamdecks)))

    for index, deck in enumerate(streamdecks):

        if deck.DECK_TYPE != 'Stream Deck +':
            print(deck.DECK_TYPE)
            print("Sorry, this script only works with Stream Deck +")
            continue

        deck.open()
        deck.reset()

        deck.set_dial_callback(dial_change_callback)
        # don't need this for now
        #deck.set_key_callback(key_change_callback)
        #deck.set_touchscreen_callback(touchscreen_event_callback)

        print("Opened '{}' device (serial number: '{}')".format(deck.deck_type(), deck.get_serial_number()))

        # Set initial screen brightness to 60%.
        deck.set_brightness(60)

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