import json
import requests
from PySide6.QtCore import Signal, QThread


from app.components.device_info import DeviceInfo
from app.common.config import cfg

class AddDeviceThread(QThread):
    finishedSignal = Signal(bool, str)

    def __init__(self, device_info: DeviceInfo):
        super().__init__()
        self.device_info = device_info
        print("AddDeviceThread init")

    def run(self):
        url = (
            "http://"
            + cfg.get(cfg.backendIP)
            + ":"
            + cfg.get(cfg.backendPort)
            + "/device/add"
        )
        data = {
            "userID": 1,
            "name": self.device_info.name,
            "ip": self.device_info.ip,
            "describe": self.device_info.describe,
        }
        device_json = json.dumps(data)
        print("prepare to try")
        try:
            response = requests.post(url, data=device_json, timeout=5)
            response.raise_for_status()
            response_data = response.json()
            data = response_data["data"]
            device = DeviceInfo(
                id=data["id"],
                name=data["name"],
                ip=data["ip"],
                describe=data["describe"],
            )
            self.finishedSignal.emit(True, device)

        except Exception as e:
            self.finishedSignal.emit(False, str(e))
