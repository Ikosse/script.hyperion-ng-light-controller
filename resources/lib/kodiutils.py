import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import os
import sys
import json


class AddonUtils():

    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.id = self.addon.getAddonInfo("id")
        self.name = self.addon.getAddonInfo("name")
        self.url = sys.argv[0]

        self.path = xbmcvfs.translatePath(self.addon.getAddonInfo("path"))
        self.profile = xbmcvfs.translatePath(self.addon.getAddonInfo("profile"))
        self.resources = os.path.join(self.path, "resources")
        self.media = os.path.join(self.resources, "media")
        self.icon = self.addon.getAddonInfo("icon")

    def localize(self, *args):
        if len(args) < 1:
            raise ValueError("String id missing")
        elif len(args) == 1:
            string_id = args[0]
            return self.addon.getLocalizedString(string_id)
        else:
            return [self.addon.getLocalizedString(string_id)
                    for string_id in args]

    def show_settings(self):
        self.addon.openSettings()

    def get_setting(self, setting):
        return self.addon.getSetting(setting).strip()

    def set_setting(self, setting, value):
        self.addon.setSetting(setting, str(value))

    def get_setting_as_bool(self, setting):
        return self.get_setting(setting).lower() == "true"

    def get_setting_as_float(self, setting):
        return float(self.get_setting(setting))

    def get_setting_as_int(self, setting):
        return int(self.get_setting_as_float(setting))
