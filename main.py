#! /usr/bin/python

import argparse
import logging
from samsungmxt40 import SamsungMXT40

ap = argparse.ArgumentParser()
ap.add_argument("-ls", "--lighting_status", required=False, help="OFF,AMBIENT,PARTY,DANCE,THUNDER,STAR,LOVER,SOLID")
ap.add_argument("-c", "--color", required=False, help="RGB separated by comma")
ap.add_argument("-t", "--tempo", required=False, type=int, help="Tempo Data")
ap.add_argument("-dj", "--dj_effect", required=False, help="DJ Effect and value separated by comma OFF,DELAY,FILTER,FLANGER,CHORUS,WAHWAH min/med/max is 1/15/30")
ap.add_argument("-b", "--bass_booster", required=False, help="ON,OFF")
ap.add_argument("-sd", "--sound", required=False, help="MORE,LESS")
ap.add_argument("-m", "--mute", required=False, action="store_true", help="Toggle mute")
ap.add_argument("-so", "--source", required=False, help="BT,USB,AUX1,AUX2")
ap.add_argument("-o", "--on_off", required=False, action="store_true", help="Turn on/off device")
ap.add_argument("-d", "--device", default="2C:FD:B3:E6:D1:08", required=False, help="serverMacAddress")
args = vars(ap.parse_args())

lighting_status = args["lighting_status"]

try:
    color = list(map(int, args["color"].split(",")))
except:
    color = None

tempo = args["tempo"]

try:
    dj_effect = args["dj_effect"].split(",")
except:
    dj_effect = None

bass_booster = args["bass_booster"]

sound = args["sound"]

source = args["source"]

device  = args["device"]

#logging.getLogger().setLevel(logging.DEBUG)
samsung = SamsungMXT40(device)
samsung.load_source_info()

if lighting_status is not None:
    samsung.effect_fragment_mode()
    print("send lighting status")
    for command in samsung.request(samsung.status_setting(lighting_status)):
        payload = SamsungMXT40.getPayloadData(command)

if color is not None:
    samsung.effect_fragment_mode()
    print("send color")
    for command in samsung.request(samsung.illumination_setting(color[0], color[1], color[2])):
        payload = SamsungMXT40.getPayloadData(command)

if tempo is not None:
    samsung.effect_fragment_mode()
    print("send tempo data")
    for command in samsung.request(samsung.tempo(tempo)):
        payload = SamsungMXT40.getPayloadData(command)

if dj_effect is not None:
    samsung.effect_fragment_mode()
    print("send dj effect")
    for command in samsung.request(samsung.change_dj_effect(dj_effect[0], int(dj_effect[1]))):
        payload = SamsungMXT40.getPayloadData(command)

if bass_booster is not None:
    samsung.effect_fragment_mode()
    print("send bass booster")
    if (bass_booster == "ON"):
        commands = samsung.request(samsung.bass_booster_on())
    elif (bass_booster == "OFF"):
        commands = samsung.request(samsung.bass_booster_off())
    for command in commands:
        payload = SamsungMXT40.getPayloadData(command)

if sound is not None:
    samsung.effect_fragment_mode()
    print("send sound")
    if (sound == "MORE"):
        commands = samsung.request(samsung.sound_more())
    elif (sound == "LESS"):
        commands = samsung.request(samsung.sound_less())
    for command in commands:
        payload = SamsungMXT40.getPayloadData(command)

if args["mute"]:
    samsung.effect_fragment_mode()
    print("toggle mute")
    for command in samsung.request(samsung.toggle_mute()):
        payload = SamsungMXT40.getPayloadData(command)

if source is not None:
    print("source_switch")
    for command in samsung.request(samsung.source_switch(source)):
        payload = SamsungMXT40.getPayloadData(command)
    if (source.startswith("AUX")):
        print("sound_setting_info")
        for command in samsung.request(samsung.sound_setting_info_req(7)):
            payload = SamsungMXT40.getPayloadData(command)
        print("sound_setting_info")
        for command in samsung.request(samsung.sound_setting_info_req(1)):
            payload = SamsungMXT40.getPayloadData(command)
        print("aux_state_req")
        for command in samsung.request(samsung.aux_state_req()):
            payload = SamsungMXT40.getPayloadData(command)
    print("usb_playtime_enable")
    if (source == "USB"):
        commands = samsung.request(samsung.usb_playtime_enable(1))
    else:
        commands = samsung.request(samsung.usb_playtime_enable(0))
    for command in commands:
        payload = SamsungMXT40.getPayloadData(command)
    if (source == "USB"):
        print("usb_status_info_req")
        for command in samsung.request(samsung.usb_status_info_req()):
            payload = SamsungMXT40.getPayloadData(command)

if args["on_off"]:
    samsung.remote_control_mode()
    print("toggle on_off")
    commands = samsung.request(samsung.toggle_on_off())
else:
    print("connect_link_restart")
    commands = samsung.request(samsung.connect_restart_req())

for command in commands:
    payload = SamsungMXT40.getPayloadData(command)

samsung.close()
