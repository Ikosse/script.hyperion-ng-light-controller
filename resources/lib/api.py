import requests
from socket import gethostname


class HyperionException(Exception):
    pass


class AuthorizationException(Exception):
    pass


def check_hyperion_status(method):
    def wrapped_method_call(*args, **kwargs):
        response_json = method(*args, **kwargs)

        if not response_json["success"]:
            if response_json["error"] == "No Authorization":
                raise AuthorizationException(response_json["error"])
            else:
                raise HyperionException(response_json["error"])
        return response_json
    return wrapped_method_call


class HyperionController():

    def __init__(self, host, port, protocol):
        self.host = host
        self.port = port
        self.url = "{0}://{1}:{2}/json-rpc".format(protocol, host, port)
        self.headers = {"Authorization": "none"}
        self.origin = gethostname()

    def set_token(self, token):
        self.headers = {"Authorization": "token " + token}

    @check_hyperion_status
    def get_server_info(self):
        payload = {
            "command": "serverinfo",
            "tan": 1
        }
        response_json = requests.post(self.url, json=payload,
                                      headers=self.headers).json()
        return response_json

    @check_hyperion_status
    def get_system_info(self):
        payload = {
            "command": "sysinfo",
            "tan": 1
        }
        response_json = requests.post(self.url, json=payload,
                                      headers=self.headers).json()
        return response_json

    @check_hyperion_status
    def set_component(self, name, state):
        payload = {
            "command": "componentstate",
            "componentstate": {
                "component": name,
                "state": state
            }
        }

        response_json = requests.post(self.url, json=payload,
                                      headers=self.headers).json()
        return response_json

    @check_hyperion_status
    def enable_effect(self, effect_name, priority=50, duration=0):
        payload = {
          "command": "effect",
          "effect": {
              "name": effect_name
          },
          "priority": priority,
          "origin": self.origin,
          "duration": duration}

        response_json = requests.post(self.url, json=payload,
                                      headers=self.headers).json()
        response_json["name"] = effect_name
        response_json["priority"] = priority

        return response_json

    @check_hyperion_status
    def enable_black_color(self):
        payload = {
          "command": "color",
          "color": [0, 0, 0],
          "priority": 1,
          "origin": self.origin}
        response_json = requests.post(self.url, json=payload,
                                      headers=self.headers).json()
        response_json["priority"] = 1
        return response_json

    @check_hyperion_status
    def select_source(self, priority):
        payload = {
           "command": "sourceselect",
           "priority": priority}
        response_json = requests.post(self.url, json=payload,
                                      headers=self.headers).json()
        return response_json

    @check_hyperion_status
    def set_black_color(self):
        response_json = self.enable_black_color()
        response_json = self.select_source(response_json["priority"])
        return response_json

    @check_hyperion_status
    def set_effect(self, name):
        response_json = self.enable_effect(name)
        response_json = self.select_source(response_json["priority"])
        return response_json

    def get_components(self):
        server_info = self.get_server_info()
        return server_info["info"]["components"]

    def get_priorities(self):
        response_json = self.get_server_info()
        return response_json["info"]["priorities"]

    def get_effects(self):
        server_info = self.get_server_info()
        return server_info["info"]["effects"]
