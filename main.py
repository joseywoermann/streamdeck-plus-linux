import os
import threading
import io

from PIL import Image
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Devices.StreamDeck import DialEventType

import subprocess

# Folder location of image assets used by this example.
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "Assets")

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
        "name": "Rocket League",
        "id": "Rocket League"
    },
    {
        "dial": 3,
        "name": "Firefox",
        "id": "Firefox"
    }
]

#
# =======================================


# callback when dials are pressed or released
def dial_change_callback(deck, dial, event, value):

    # Application mute
    if event == DialEventType.PUSH:

        if value:
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

                    # toggle mute state
                    subprocess.run(["wpctl", "set-mute", node_id, "toggle"], stdout=subprocess.PIPE)
                    print(f"Toggled {programs[dial]["name"]}'s mute state. [Pipewire Node ID: {node_id}]")


    # Application vlume control +/-
    elif event == DialEventType.TURN:

        # change volume by +/-2% at a time
        if value < 0:
            value = -2
        else:
            value = 2

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


def key_change_callback(deck, key, state):

    if state:
        if key == 0:
            # Mute default microphone
            # Run wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle
            subprocess.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SOURCE@", "toggle"], stdout=subprocess.PIPE)

        elif key == 7:
            # reset deck and wuit script
            deck.reset()
            deck.close()


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

        # register callback functions
        deck.set_dial_callback(dial_change_callback)
        deck.set_key_callback(key_change_callback)

        print(f"Opened {deck.deck_type()} | Serial number: '{deck.get_serial_number()}')")

        # Set initial screen brightness to 60%.
        deck.set_brightness(60)


      
        # build an image for the touch lcd
        img = Image.new('RGB', (800, 100), 'black')
        icon = Image.open(os.path.join(ASSETS_PATH, 'touch_bg.png')).resize((800, 100))
        img.paste(icon, (0, 0), icon)

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