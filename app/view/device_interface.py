import threading
import requests
from qfluentwidgets import ScrollArea, InfoBar, InfoBarPosition
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, QCoreApplication, QSettings, QMetaObject, Q_ARG, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGraphicsView
from ..components.device_info import DeviceInfo
from ..components.device_card import DeviceCardView
from ..common.style_sheet import StyleSheet

class DeviceInterface(ScrollArea):
    addDeviceCardSignal = Signal(DeviceInfo)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.deviceCardView = DeviceCardView(self.tr("Device"), self)
        self.vBoxLayout.addWidget(self.deviceCardView)
        self.vBoxLayout.addStretch(1)

        self.__initSlot()
        self.__initWidget()
        
    def __initSlot(self):
        self.addDeviceCardSignal.connect(lambda device_info: self.deviceCardView.addDeviceCard(device_info))

    def __initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        StyleSheet.DEVICE_INTERFACE.apply(self)
        load_device_thread = threading.Thread(target=self.load_device_info)
        load_device_thread.start()
        
    def load_device_info(self):
        url = "http://127.0.0.1:15565/device/get/1"
        try:
            response = requests.get(url)
            response.raise_for_status()  # This will raise an exception if the request was not successful (status code other than 200)
            
            json_data = response.json()
            data_array = json_data["data"]

            device_info_list = []
            for item in data_array:
                id = item["id"]
                name = item["name"]
                ip = item["ip"]
                describe = item["describe"]

                device_info = DeviceInfo(id=id, name=name, ip=ip, describe=describe)
                self.addDeviceCardSignal.emit(device_info)

        except requests.exceptions.RequestException as e:
            QMetaObject.invokeMethod(self, "showErrorMessage", Qt.ConnectionType.QueuedConnection, Q_ARG(str, "请求错误：无法连接到服务器"))


        except ValueError as e:
            QMetaObject.invokeMethod(self, "showErrorMessage", Qt.ConnectionType.QueuedConnection, Q_ARG(str, "无效的 JSON 数据"))

        except Exception as e:
            QMetaObject.invokeMethod(self, "showErrorMessage", Qt.ConnectionType.QueuedConnection, Q_ARG(str, "发生了意外错误"))
            
    @Slot(str)
    def showErrorMessage(self, message):
        InfoBar.error(
            title=self.tr('Error'),
            content=self.tr(message),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )