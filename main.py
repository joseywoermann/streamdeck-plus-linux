import os
import threading
import io

from PIL import Image
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices.StreamDeck import DialEventType, TouchscreenEventType

import subprocess



# =======================================
#
# TODO: move this to a config.json
programs = [
    {
        "dial": 0,
        "name": "Spotify",
        "id": "spotify"
    },
    {
        "dial": 1,
        "name": "Feishin",
        "id": "Chromium"
    },
    {
        "dial": 2,
        "name": "GTA V",
        "id": "Grand Theft Auto V"
    },
    {
        "dial": 3,
        "name": "Minecraft",
        "id": "java"
    }
]

#
# =======================================


# callback when dials are pressed or released
def dial_change_callback(deck, dial, event, value):
    if event == DialEventType.PUSH:
        print(f"dial pushed: {dial} state: {value}")

        if dial == 3 and value:
            deck.reset()
            deck.close()

    elif event == DialEventType.TURN:
        #print(f"dial {dial} turned: {value}")

        # change volume by +/-2% at a time
        if value < 0:
            value = -2
        else:
            value = 2

        dial_volume_control(dial, value)

# Adjust the volume of the program mapped to the dial
def dial_volume_control(dial, value):

    # run "wpctl status" and return its output
    wpctl_shell_out = subprocess.run(["wpctl", "status"], stdout=subprocess.PIPE)
    wpctl_string = wpctl_shell_out.stdout.decode("utf-8")

    # find the line with the program's id
    for line in wpctl_string.split("\n"):
        if programs[dial]["id"] in line and not "pid:" in line:

            # extract the digits from the line
            shell_list = list(line)
            for i in shell_list:
                if i == " ":
                    shell_list.remove(i)
            node_id = "".join(shell_list).split(".")[0]

            # get current app volume
            wpctl_shell_out1 = subprocess.run(["wpctl", "get-volume", node_id], stdout=subprocess.PIPE)
            program_volume = float(wpctl_shell_out1.stdout.decode("utf-8")[8:])*100
            
            if program_volume + float(value) > 100: 
                print("Cannot set volume to higher than 100.")
            elif program_volume + float(value) < 0:
                print("Cannot set volume to below 0.")
            else:
                program_volume = program_volume + float(value)
                subprocess.run(["wpctl", "set-volume", node_id, f"{str(program_volume)}%"], stdout=subprocess.PIPE)
                print(f"Set {programs[dial]["name"]} volume to {program_volume}. [Pipewire Node ID: {node_id}]")

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

        print(f"Opened '{deck.deck_type()}' device (serial number: '{deck.get_serial_number()}')")

        # Set initial screen brightness to 60%.
        deck.set_brightness(60)

        # Wait until all application threads have terminated (for this example,
        # this is when all deck handles are closed).
        for t in threading.enumerate():
            try:
                t.join()
            except RuntimeError:
                pass