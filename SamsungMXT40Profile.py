from samsungmxt40 import SamsungMXT40
from typing import List

from blueman.Functions import create_menuitem
from blueman.bluez.Device import Device
from blueman.plugins.ManagerPlugin import ManagerPlugin
from blueman.gui.manager.ManagerDeviceMenu import ManagerDeviceMenu, MenuItemsProvider, DeviceMenuItem

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from datetime import datetime
import time


def create_txt_menuitem(text: str) -> Gtk.MenuItem:
    item = Gtk.MenuItem(label=text, use_underline=True)
    child = item.get_child()
    assert isinstance(child, Gtk.AccelLabel)
    child.set_use_markup(True)
    item.show_all()

    return item

class SamsungMXT40Profile(ManagerPlugin, MenuItemsProvider):
    name = "[AV] MX-T40"

    def on_load(self) -> None:
        self.devices: Dict[str, "Info"] = {}

    def generate_source_menu(self, device: Device, item: Gtk.MenuItem) -> None:
        try:
            samsung = self.devices[device['Address']]
        except KeyError:
            self.devices[device['Address']] = SamsungMXT40(device['Address'])
            samsung = self.devices[device['Address']]
        group: Sequence[Gtk.RadioMenuItem] = []

        sub = Gtk.Menu()

        if (samsung.source_updated_at is None) or (datetime.now() - samsung.source_updated_at).seconds > 10:
            samsung.connect()
            samsung.load_source_info()
            samsung.close()

        for source in samsung.source_info:
            i = Gtk.RadioMenuItem.new_with_label(group, source)
            group = i.get_group()

            if source == samsung.source_label:
                i.set_active(True)

            i.connect("toggled", self.on_source_selection_changed,
                      device, source)

            sub.append(i)
            i.show()

        item.set_submenu(sub)
        item.show()

    def generate_sound_menu(self, samsung: SamsungMXT40, item: Gtk.MenuItem) -> None:
        sub = Gtk.Menu()
        item_sound_more_5 = create_menuitem("Sound More 5", "audio-volume-high")
        item_sound_more_5.props.tooltip_text = "Increase Sound 5 times"
        item_sound_more_5.connect('activate', lambda x: SamsungMXT40Profile.sound_more(samsung, 5))
        sub.append(item_sound_more_5)

        item_sound_more = create_menuitem("Sound More", "audio-volume-high")
        item_sound_more.props.tooltip_text = "Increase Sound 1 time"
        item_sound_more.connect('activate', lambda x: SamsungMXT40Profile.sound_more(samsung, 1))
        sub.append(item_sound_more)

        item_sound_less = create_menuitem("Sound Less", "audio-volume-low")
        item_sound_less.props.tooltip_text = "Decrease Sound 1 time"
        item_sound_less.connect('activate', lambda x: SamsungMXT40Profile.sound_less(samsung, 1))
        sub.append(item_sound_less)

        item_sound_less_5 = create_menuitem("Sound Less 5", "audio-volume-low")
        item_sound_less_5.props.tooltip_text = "Decrease Sound 5 times"
        item_sound_less_5.connect('activate', lambda x: SamsungMXT40Profile.sound_less(samsung, 5))
        sub.append(item_sound_less_5)

        item.set_submenu(sub)
        item.show()

    def generate_light_menu(self, samsung: SamsungMXT40, item: Gtk.MenuItem) -> None:
        sub = Gtk.Menu()

        for label in samsung.status_map:
            i = create_txt_menuitem(label)
            i.props.tooltip_text = label
            i.connect('activate', SamsungMXT40Profile.on_change_status, samsung, label)
            sub.append(i)

        item.set_submenu(sub)
        item.show()

    def generate_dj_effect_menu(self, samsung: SamsungMXT40, item: Gtk.MenuItem) -> None:
        sub = Gtk.Menu()

        for label in samsung.effect_map:
            i = create_txt_menuitem(label)
            i.props.tooltip_text = label
            if (label == "OFF"):
                i.connect('activate', SamsungMXT40Profile.on_change_dj_effect, samsung, label, 1)
            else:
                self.generate_dj_effect_value_menu(samsung, i, label)
            sub.append(i)

        i = create_txt_menuitem("Tempo")
        i.props.tooltip_text = "Tempo"
        self.generate_tempo_menu(samsung, i)
        sub.append(i)

        item.set_submenu(sub)
        item.show()

    def generate_dj_effect_value_menu(self, samsung: SamsungMXT40, item: Gtk.MenuItem, label: str) -> None:
        sub = Gtk.Menu()

        for value in range(1, 31):
            i = create_txt_menuitem(value)
            i.props.tooltip_text = label + " " + str(value)
            i.connect('activate', SamsungMXT40Profile.on_change_dj_effect, samsung, label, value)
            sub.append(i)

        item.set_submenu(sub)
        item.show()

    def generate_tempo_menu(self, samsung: SamsungMXT40, item: Gtk.MenuItem) -> None:
        sub = Gtk.Menu()

        for value in range(16):
            i = create_txt_menuitem(value)
            i.props.tooltip_text = str(value)
            i.connect('activate', SamsungMXT40Profile.on_change_tempo, samsung, value)
            sub.append(i)

        item.set_submenu(sub)
        item.show()

    def generate_bass_booster_menu(self, samsung: SamsungMXT40, item: Gtk.MenuItem) -> None:
        sub = Gtk.Menu()

        for label in ["ON", "OFF"]:
            i = create_txt_menuitem(label)
            i.props.tooltip_text = label
            i.connect('activate', SamsungMXT40Profile.on_change_bass_booster, samsung, label)
            sub.append(i)

        item.set_submenu(sub)
        item.show()

    def on_source_selection_changed(self, item: Gtk.CheckMenuItem, device: Device, source: str) -> None:
        if item.get_active():
            samsung = self.devices[device['Address']]
            samsung.connect()
            samsung.load_source_info()
            if source == "OFF":
                samsung.remote_control_mode()
                commands = samsung.request(samsung.toggle_on_off())
            else:
                samsung.request(samsung.source_switch(source))
                if (source.startswith("AUX")):
                    samsung.request(samsung.sound_setting_info_req(7))
                    samsung.request(samsung.sound_setting_info_req(1))
                    samsung.request(samsung.aux_state_req())
                elif (source.startswith("USB")):
                    samsung.request(samsung.usb_playtime_enable(1))
                    samsung.usb_status_info_req()
                else:
                    samsung.request(samsung.usb_playtime_enable(0))
                samsung.request(samsung.connect_restart_req())
            samsung.close()

    def on_change_status(item: Gtk.MenuItem, samsung: SamsungMXT40, label: str) -> None:
        samsung.connect()
        samsung.load_source_info()
        samsung.effect_fragment_mode()
        samsung.request(samsung.status_setting(label))
        samsung.close()

    def on_change_dj_effect(item: Gtk.MenuItem, samsung: SamsungMXT40, label: str, value: int) -> None:
        samsung.connect()
        samsung.load_source_info()
        samsung.effect_fragment_mode()
        samsung.request(samsung.change_dj_effect(label, value))
        samsung.close()

    def on_change_tempo(item: Gtk.MenuItem, samsung: SamsungMXT40, value: int) -> None:
        samsung.connect()
        samsung.load_source_info()
        samsung.effect_fragment_mode()
        samsung.request(samsung.tempo(value))
        samsung.close()

    def on_change_bass_booster(item: Gtk.MenuItem, samsung: SamsungMXT40, label: str) -> None:
        samsung.connect()
        samsung.load_source_info()
        samsung.effect_fragment_mode()
        if (label == "ON"):
            samsung.request(samsung.bass_booster_on())
        elif (label == "OFF"):
            samsung.request(samsung.bass_booster_off())
        samsung.close()

    def sound_more(samsung: SamsungMXT40, times: int) -> None:
        samsung.connect()
        samsung.effect_fragment_mode()
        for i in range(times):
            samsung.request(samsung.sound_more())
        samsung.request(samsung.connect_restart_req())
        samsung.close()

    def sound_less(samsung: SamsungMXT40, times: int) -> None:
        samsung.connect()
        samsung.effect_fragment_mode()
        for i in range(times):
            samsung.request(samsung.sound_less())
        samsung.request(samsung.connect_restart_req())
        samsung.close()

    def color_picker(samsung: SamsungMXT40, parent: Gtk.Window) -> None:
        dialog = Gtk.ColorSelectionDialog(title='Select color')
        dialog.set_transient_for(parent)
        colorsel = dialog.get_color_selection()
        colorsel.set_has_palette(False)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            color = colorsel.get_current_rgba()
            dialog.destroy()
            samsung.connect()
            samsung.effect_fragment_mode()
            samsung.request(samsung.illumination_setting(int(color.red * 10), int(color.green * 10), int(color.blue * 10)))
            samsung.close()
        else:
            dialog.destroy()

    def toggle_mute(samsung: SamsungMXT40) -> None:
        samsung.connect()
        samsung.effect_fragment_mode()
        commands = samsung.request(samsung.toggle_mute())
        samsung.request(samsung.connect_restart_req())
        samsung.close()

    def on_request_menu_items(self, manager_menu: ManagerDeviceMenu, device: Device, _powered: bool) -> List[DeviceMenuItem]:
        if self.name == device['Name']:
            _window = manager_menu.get_toplevel()
            assert isinstance(_window, Gtk.Window)
            window = _window  # https://github.com/python/mypy/issues/2608

            item_source = create_menuitem("Source", "audio-card")
            item_source.props.tooltip_text = "Select audio source"
            self.generate_source_menu(device, item_source)
            samsung = self.devices[device['Address']]

            item_sound = create_menuitem("Change Sound Volume", "audio-speakers")
            item_sound.props.tooltip_text = "Change Sound Volume"
            self.generate_sound_menu(samsung, item_sound)

            item_light = create_txt_menuitem("Change Light")
            item_light.props.tooltip_text = "Change Light status"
            self.generate_light_menu(samsung, item_light)

            item_color = create_txt_menuitem("Change Color")
            item_color.props.tooltip_text = "Change color"
            item_color.connect('activate', lambda x: SamsungMXT40Profile.color_picker(samsung, window))

            item_dj_effect = create_txt_menuitem("Change DJ Effect")
            item_light.props.tooltip_text = "Change DJ Effect"
            self.generate_dj_effect_menu(samsung, item_dj_effect)

            item_bass_booster = create_txt_menuitem("Change Bass Booster")
            item_bass_booster.props.tooltip_text = "Change Bass Booster"
            self.generate_bass_booster_menu(samsung, item_bass_booster)

            item_toggle_mute = create_menuitem("Toggle Mute", "audio-volume-muted")
            item_toggle_mute.props.tooltip_text = "Toggle Mute Device"
            item_toggle_mute.connect('activate', lambda x: SamsungMXT40Profile.toggle_mute(samsung))

            return [DeviceMenuItem(item_source, DeviceMenuItem.Group.ACTIONS, 500), DeviceMenuItem(item_sound, DeviceMenuItem.Group.ACTIONS, 500),
                    DeviceMenuItem(item_light, DeviceMenuItem.Group.ACTIONS, 500), DeviceMenuItem(item_color, DeviceMenuItem.Group.ACTIONS, 500),
                    DeviceMenuItem(item_dj_effect, DeviceMenuItem.Group.ACTIONS, 500), DeviceMenuItem(item_bass_booster, DeviceMenuItem.Group.ACTIONS, 500),
                    DeviceMenuItem(item_toggle_mute, DeviceMenuItem.Group.ACTIONS, 500)]
        return []
