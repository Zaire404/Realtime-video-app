# coding:utf-8
import requests
import json
import threading
from PySide6.QtCore import Qt, Signal, QMetaObject, Q_ARG, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout

from qfluentwidgets import TextWrap, FlowLayout, TransparentPushButton, MessageBox, InfoBar, InfoBarPosition
from qfluentwidgets import FluentIcon as FIF
from ..components.device_info import DeviceInfo
from ..components.device_dialog import DeviceDialog
from ..common.style_sheet import StyleSheet
from ..common.config import cfg


class DeviceCard(QFrame):
    """ Device card """

    def __init__(self, device_info: DeviceInfo, parent=None):
        super().__init__(parent=parent)
        self.device_info = device_info
        self.nameLabel = QLabel(self.device_info.name, self)
        self.ipLabel = QLabel(self.device_info.ip, self)
        self.contentLabel = QLabel(TextWrap.wrap(self.device_info.describe, 45, False)[0], self)
        self.vBoxLayout = QVBoxLayout(self)
        self.hBoxLayout = QHBoxLayout()
        self.playButton = TransparentPushButton("Play", self, FIF.SEND)
        self.editButton = TransparentPushButton("Edit", self, FIF.EDIT)
        self.deleteButton = TransparentPushButton("Delete", self, FIF.DELETE)
        
        self.setFixedSize(360, 220)
        
        self.nameLabel.setObjectName('nameLabel')
        self.ipLabel.setObjectName('ipLabel')
        self.contentLabel.setObjectName('contentLabel')
        self.playButton.setObjectName('playButton')
        self.editButton.setObjectName('editButton')
        self.deleteButton.setObjectName('deleteButton')
        
        self.editButton.clicked.connect(self.showDeviceDialog)
        self.deleteButton.clicked.connect(self.deleteDevice)
        self.playButton.clicked.connect(self.on_playButton_clicked)
        self.__initLayout()
    
    def __initLayout(self):
        self.vBoxLayout.setSpacing(5)
        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.hBoxLayout.setSpacing(30)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        self.vBoxLayout.addWidget(self.nameLabel)
        self.vBoxLayout.addWidget(self.ipLabel)
        self.vBoxLayout.addWidget(self.contentLabel)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addLayout(self.hBoxLayout)
        
        self.hBoxLayout.addWidget(self.playButton)
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.editButton)
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.deleteButton)
    
    def showDeviceDialog(self):
        w = DeviceDialog(self.device_info, parent = self.window())
        w.yesSignal.connect(self.updateDevice)
        if w.exec():
            print('Yes button is pressed')
        else:
            print('Cancel button is pressed')
        
    def updateUI(self):
        self.nameLabel.setText(self.device_info.name)
        self.ipLabel.setText(self.device_info.ip)
        self.contentLabel.setText(self.device_info.describe)
    
    def updateDevice(self, device_info: DeviceInfo): 
        self.device_info = device_info        
        url = "http://" + cfg.get(cfg.backendIP) + ":" + cfg.get(cfg.backendPort) + "/device/update"
        data = device_info.__dict__()
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)     
        if response.status_code == 200:
            self.updateUI()
            InfoBar.success(
                title=self.tr('Success'),
                content=self.tr("操作成功"),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self.parent
            )
        else:
            InfoBar.error(
                title=self.tr('Error'),
                content=self.tr("请求错误"),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self.parent
            )
    
    def deleteDevice(self):
        w = MessageBox("删除", "删除后无法恢复, 是否确认删除?", self.window())
        if w.exec():
            url = "http://" + cfg.get(cfg.backendIP) + ":" + cfg.get(cfg.backendPort) + "/device/delete"
            data = {'deviceID': self.device_info.id}
            headers = {'Content-type': 'application/json'}

            response = requests.post(url, data=json.dumps(data), headers=headers)
            if response.status_code == 200:
                InfoBar.success(
                    title=self.tr('Success'),
                    content=self.tr("操作成功"),
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
            else:
                InfoBar.error(
                    title=self.tr('Error'),
                    content=self.tr("请求错误"),
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
                return 
        else:
            return
        self.deleteLater()
            
    def on_playButton_clicked():
        #Todo
        return 
        
            
class DeviceCardView(QWidget):
    """ Device card view """
    deviceAdded = Signal(DeviceInfo)
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)
        self.titleLabel = QLabel(title, self)
        self.vBoxLayout = QVBoxLayout(self)
        self.device_flowLayout = FlowLayout()
        self.tool_flowLayout = FlowLayout()
        self.addButton = TransparentPushButton("Add", self, FIF.ADD)
        
        self.__initLayout()

        self.addButton.clicked.connect(self.showDeviceDialog)
        
        self.titleLabel.setObjectName('viewTitleLabel')
        self.addButton.setObjectName('addButton')
        StyleSheet.DEVICE_CARD.apply(self)
        
    def __initLayout(self):
        self.vBoxLayout.setContentsMargins(36, 0, 36, 0)
        self.vBoxLayout.setSpacing(10)
        self.device_flowLayout.setContentsMargins(0, 0, 0, 0)
        self.device_flowLayout.setHorizontalSpacing(12)
        self.device_flowLayout.setVerticalSpacing(12)
        self.tool_flowLayout.addWidget(self.addButton)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addLayout(self.tool_flowLayout)
        self.vBoxLayout.addLayout(self.device_flowLayout)
        # self.vBoxLayout.addLayout(self.device_flowLayout, 1)
        
    def addDeviceCard(self, device_info: DeviceInfo):
        card = DeviceCard(device_info, self)
        self.device_flowLayout.addWidget(card)
        self.deviceAdded.emit(device_info)


    def showDeviceDialog(self):
        w = DeviceDialog(device_info = DeviceInfo(), parent = self.window())
        w.yesSignal.connect(self.addDevice)
        if w.exec():
            # TODO: interact with golang 
            print('Yes button is pressed')
        else:
            print('Cancel button is pressed')
            
    def addDevice(self, device_info: DeviceInfo):
        url = "http://" + cfg.get(cfg.backendIP) + ":" + cfg.get(cfg.backendPort) + "/device/add"
        data = {
            "userID": 1,
            "name": device_info.name,
            "ip": device_info.ip,
            "Describe": device_info.describe
        }
        device_json = json.dumps(data)

        try:
            response = requests.post(url, data=device_json)
            response.raise_for_status()  # This will raise an exception if the request was not successful (status code other than 200)

            response_data = response.json()
            data = response_data["data"]
            device = DeviceInfo(
                id=data["id"],
                name=data["name"],
                ip=data["ip"],
                describe=data["describe"]
            )
            self.addDeviceCard(device)
            InfoBar.success(
                title=self.tr('Success'),
                content=self.tr("操作成功"),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )

        except requests.exceptions.RequestException as e:
            # This exception will be raised for any error that occurred during the request (connection error, timeout, etc.)
            InfoBar.error(
                title=self.tr('Error'),
                content=self.tr("请求错误"),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )

        except ValueError as e:
            # This exception will be raised if there is an error parsing the JSON data (invalid JSON format)
            InfoBar.error(
                title=self.tr('Error'),
                content=self.tr("无效的 JSON 数据"),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )

        except Exception as e:
            # Handle any other unexpected exceptions here
            InfoBar.error(
                title=self.tr('Error'),
                content=self.tr("发生未知错误"),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )

        
