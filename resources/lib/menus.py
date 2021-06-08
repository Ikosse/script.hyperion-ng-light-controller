import time
import xbmcgui
from requests.exceptions import ConnectionError
from resources.lib.kodiutils import AddonUtils
from resources.lib.api import HyperionController, HyperionException, \
        AuthorizationException


class MenuList():

    UPDATE_DELAY = 0.35  # Small delay added to make sure the server updates
    # before querying new information.

    def __init__(self):
        self.addon_utils = AddonUtils()
        host = self.addon_utils.get_setting("address")
        port = self.addon_utils.get_setting_as_int("port")
        protocol = self.addon_utils.get_setting("protocol")
        token = self.addon_utils.get_setting("token")

        self.hyperion_controller = HyperionController(host, port, protocol)
        self.hyperion_controller.origin = "Kodi"
        self.hyperion_controller.set_token(token)

    def _hyperion_error_check(self, hyperion_method, *args, **kwargs):
        header = "{0} - {1}".format(
            self.addon_utils.name, self.addon_utils.localize(30100)
        )
        try:
            response_json = hyperion_method(*args, **kwargs)
        except AuthorizationException:
            xbmcgui.Dialog().textviewer(
                header, self.addon_utils.localize(30101)
            )
        except HyperionException as e:
            xbmcgui.Dialog().textviewer(header, str(e))
            raise
        except ConnectionError:
            error_msg = "{0} {1}. {2}".format(
                self.addon_utils.localize(30102), self.hyperion_controller.url,
                self.addon_utils.localize(30103)
            )
            xbmcgui.Dialog().textviewer(header, error_msg)
            raise
        except Exception:
            xbmcgui.Dialog().textviewer(
                header, self.addon_utils.localize(30104)
            )
            raise
        else:
            return response_json

    def main_menu(self):
        header = self.addon_utils.name

        exit_menu = False
        choice = 0
        while not exit_menu:
            menu_items = self.addon_utils.localize(
                    30000, 30001, 30002, 30003, 30004)

            choice = xbmcgui.Dialog().select(header, menu_items,
                                             preselect=choice)

            if choice == 0:
                self._hyperion_error_check(
                    self.hyperion_controller.set_black_color)
            elif choice == 1:
                self.selection_menu()
            elif choice == 2:
                self.effects_menu()
            elif choice == 3:
                self.components_menu()
            elif choice == 4:
                self.show_hyperion_info()
            else:
                exit_menu = True

    def selection_menu(self):
        header = "{0} - {1}".format(self.addon_utils.name,
                                    self.addon_utils.localize(30001))

        exit_menu = False
        while not exit_menu:
            selections = self._hyperion_error_check(
                self.hyperion_controller.get_priorities)

            menu_items = ["[COLOR {0}]{1}[/COLOR]".format(
                "green" if item["visible"] else
                "blue" if item["active"] else
                "red", item["componentId"])
                for item in selections]

            choice = xbmcgui.Dialog().select(header, menu_items)

            if choice == -1:
                exit_menu = True
            else:
                self._hyperion_error_check(
                    self.hyperion_controller.select_source,
                    selections[choice]["priority"])
                time.sleep(self.UPDATE_DELAY)

    def effects_menu(self):
        header = "{0} - {1}".format(self.addon_utils.name,
                                    self.addon_utils.localize(30002))

        exit_menu = False
        choice = 0
        while not exit_menu:
            effects = self._hyperion_error_check(
                self.hyperion_controller.get_effects)

            menu_items = [effect["name"] for effect in effects]

            choice = xbmcgui.Dialog().select(header, menu_items,
                                             preselect=choice)

            if choice == -1:
                exit_menu = True
            else:
                self._hyperion_error_check(
                    self.hyperion_controller.set_effect, menu_items[choice])
                time.sleep(self.UPDATE_DELAY)

    def components_menu(self):
        header = "{0} - {1}".format(self.addon_utils.name,
                                    self.addon_utils.localize(30003))

        exit_menu = False
        choice = 0
        while not exit_menu:
            components = self._hyperion_error_check(
                self.hyperion_controller.get_components)

            menu_items = ["[COLOR {0}]{1}[/COLOR]".format(
                "green" if component["enabled"] else
                "red", component["name"])
                for component in components]

            choice = xbmcgui.Dialog().select(header, menu_items,
                                             preselect=choice)

            if choice == -1:
                exit_menu = True
            else:
                self._hyperion_error_check(
                    self.hyperion_controller.set_component,
                    components[choice]["name"],
                    not components[choice]["enabled"])
                time.sleep(self.UPDATE_DELAY)

    def show_hyperion_info(self):
        header = "{0} - {1}".format(self.addon_utils.name,
                                    self.addon_utils.localize(30004))
        sys_info = self._hyperion_error_check(
            self.hyperion_controller.get_system_info
        )["info"]["hyperion"]

        info_str = ""
        for (key, val) in sys_info.items():
            info_str = info_str \
                + "[COLOR blue]{0}[/COLOR]: {1}\n".format(key, val)
        xbmcgui.Dialog().textviewer(header, info_str)
