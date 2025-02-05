import subprocess
import re

class AdbController:
    current_device_name = None

    def __init__(self, app_name : str, app_host_path : str, accessibility_service_name : str,
                 recording_component_name : str, broadcast_component_name : str, broadcast_intent : str) -> None:
        self.app_name = app_name
        self.app_host_path = app_host_path
        self.service_name = f"{self.app_name}/.{accessibility_service_name}"
        self.recording_component = f"{self.app_name}/.{recording_component_name}"
        self.broadcast_component = f"{self.app_name}/.{broadcast_component_name}"
        self.broadcast_intent = broadcast_intent

    def get_connected_devices(self):
        result = []
        output = self._adb("devices")
        for line in output.split("\n"):
            match = re.match("^([a-zA-Z0-9\\-]+)(\\s+)(device)", line)
            if match is not None:
                result.append(match.group(1))
        return result
    
    def set_current_device_name(self, name):
        self.current_device_name = name
    
    def check_app_exists(self):
        return self.app_name in self._adb_s("shell pm list packages")
    
    def is_app_running(self):
        try:
            self._adb_s(f"shell pidof {self.app_name}")
            return True
        except subprocess.CalledProcessError:
            return False  # Exception if no such process
    
    def get_screen_resolution(self):
        try:
            output = self._adb_s("shell wm size")
            numbers = [int(entry) for entry in re.findall(r"\d+", output)]
            assert len(numbers) == 2  # Width and height
            return numbers
        except subprocess.CalledProcessError as e:
            print(f"Get screen resolution error: {e}")
    
    def install_app(self):
        try:
            self._adb_s(f"install -g {self.app_host_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Install app error: {e}")
            return False
        
    def start_app(self):
        self._enable_port_forwarding(1935) # RTMP
        self._enable_port_forwarding(1936) # TCP
        # The first action is starting AS to put a trigger on button_1 element
        # which is a "Start" streaming button
        self._disable_accessibility()
        self._enable_accessibility()
        # Then launch the component which is going to show the permission dialog
        # The "Start" button will be clicked automatically almost immediatelly after start
        self._launch_recording_component()
        
    def request_transmission(self, mode):
        if not self.is_app_running():
            self.start_app()
        self._send_broadcast("mode", mode)
        
    def _launch_recording_component(self):
        try:
            self._adb_s(f"shell am start -n {self.recording_component}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Launch component error: {e}")
            return False
    
    def _enable_accessibility(self):
        try:
            setting = self._get_secure_settings()["enabled_accessibility_services"]
            if self.service_name in setting:
                print("Accessibility is already enabled")
                return True
            new_value = setting + (":" if len(setting) > 0 else "") + self.service_name
            self._adb_s(f"shell settings put secure enabled_accessibility_services {new_value}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Enable accessibility error: {e}")
            return False

    def _disable_accessibility(self):   
        try:     
            setting = self._get_secure_settings()["enabled_accessibility_services"]
            if self.service_name not in setting:
                print("Accessibility is not enabled")
                return True
            # Dont care about colons
            new_value = setting.replace(self.service_name, "")
            if len(new_value) == 0:
                new_value = "null"
            self._adb_s(f"shell settings put secure enabled_accessibility_services {new_value}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Disable accessibility error: {e}")
            return False

    def _adb(self, command : str) -> str:
        return subprocess.check_output((f"adb {command}").split()).decode()

    def _adb_s(self, command : str) -> str:
        if self.current_device_name is None:
            raise "ADB device is not chosen"
        return self._adb(f"-s {self.current_device_name} {command}")

    def _get_secure_settings(self):
        output = self._adb_s("shell settings list secure")
        return {value[0]: value[1] for value in [line.split("=", 2) for line in output.splitlines()]}
    
    def _enable_port_forwarding(self, port_num):
        try:
            self._adb_s(f"reverse tcp:{port_num} tcp:{port_num}")
        except subprocess.CalledProcessError as e:
            print(f"Port (reverse) forwarding error: {e}")

    def _send_broadcast(self, extra_name : str, extra_message : str):
        try:
            self._adb_s(f"shell am broadcast -a {self.broadcast_intent} --es {extra_name} {extra_message} -n {self.broadcast_component}")
        except subprocess.CalledProcessError as e:
            print(f"Send broadcast error: {e}")
