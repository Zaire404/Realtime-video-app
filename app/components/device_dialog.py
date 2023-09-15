import re
from PySide6.QtCore import Qt, Signal, QObject, QEvent
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout, QHBoxLayout, QPushButton
from qframelesswindow import FramelessDialog

from qfluentwidgets import TextWrap, PrimaryPushButton, LineEdit, TextEdit, InfoBar, InfoBarPosition
from qfluentwidgets.components.dialog_box.mask_dialog_base import MaskDialogBase
from ..components.device_info import DeviceInfo
from ..common.style_sheet import StyleSheet

# device_name  device_ip describe
class Ui_DeviceDialog:
    """ Ui of message box """

    yesSignal = Signal(DeviceInfo)
    cancelSignal = Signal()

    def __init__(self, *args, **kwargs):
        pass

    def _setUpUi(self, device_info: DeviceInfo, parent = None):
        self.device_info = device_info
        
        # 这边为什么用parent?
        self.nameLabel = QLabel('Device Name *', parent)
        self.ipLabel = QLabel('Device IP *', parent)
        self.describeLabel = QLabel('Describe', parent)
        self.nameLineEdit = LineEdit(self)
        self.ipLineEdit = LineEdit(self)
        self.describeLineEdit = TextEdit(self)
        
        
        self.buttonGroup = QFrame(parent)
        self.yesButton = PrimaryPushButton(self.tr('OK'), self.buttonGroup)
        self.cancelButton = QPushButton(self.tr('Cancel'), self.buttonGroup)

        self.vBoxLayout = QVBoxLayout(parent)
        self.contentLayout = QVBoxLayout()
        # self.textLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout(self.buttonGroup)

        self.__initWidget()

    def __initWidget(self):
        self.nameLineEdit.setText(self.device_info.name)
        self.nameLineEdit.setPlaceholderText("device in home")
        self.nameLineEdit.setClearButtonEnabled(True)
        self.ipLineEdit.setText(self.device_info.ip)
        self.ipLineEdit.setPlaceholderText("xx.xx.xx.xx")
        self.ipLineEdit.setClearButtonEnabled(True)
        self.describeLineEdit.setMarkdown(self.device_info.describe)
        self.describeLineEdit.setPlaceholderText("something about the device")
        self.describeLineEdit.setFixedHeight(100)
        self.__setQss()
        self.__initLayout()

        self.yesButton.setAttribute(Qt.WA_LayoutUsesWidgetRect)
        self.cancelButton.setAttribute(Qt.WA_LayoutUsesWidgetRect)

        self.yesButton.setFocus()
        self.buttonGroup.setFixedHeight(81)

        # self._adjustText()

        self.yesButton.clicked.connect(self.__onYesButtonClicked)
        self.cancelButton.clicked.connect(self.__onCancelButtonClicked)

    def _adjustText(self):
        if self.isWindow():
            if self.parent():
                w = max(self.titleLabel.width(), self.parent().width())
                chars = max(min(w / 9, 140), 30)
            else:
                chars = 100
        else:
            w = max(self.titleLabel.width(), self.window().width())
            chars = max(min(w / 9, 100), 30)

        self.contentLabel.setText(TextWrap.wrap(self.content, chars, False)[0])

    def __initLayout(self):
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addLayout(self.contentLayout, 1)
        self.vBoxLayout.addWidget(self.buttonGroup, 0, Qt.AlignBottom)
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        
        self.contentLayout.setSpacing(12)
        self.contentLayout.setContentsMargins(24, 24, 24, 24)   
        self.contentLayout.addWidget(self.nameLabel)
        self.contentLayout.addWidget(self.nameLineEdit)
        self.contentLayout.addWidget(self.ipLabel)
        self.contentLayout.addWidget(self.ipLineEdit)
        self.contentLayout.addWidget(self.describeLabel)
        self.contentLayout.addWidget(self.describeLineEdit)
        
        self.buttonLayout.setSpacing(12)
        self.buttonLayout.setContentsMargins(24, 24, 24, 24)
        self.buttonLayout.addWidget(self.yesButton, 1, Qt.AlignVCenter)
        self.buttonLayout.addWidget(self.cancelButton, 1, Qt.AlignVCenter)

    def __onCancelButtonClicked(self):
        self.reject()
        self.cancelSignal.emit()

    def __onYesButtonClicked(self):
        success, err = self.checkValid()
        if success:
            self.accept()
            self.device_info.name = self.nameLineEdit.text()
            self.device_info.ip = self.ipLineEdit.text()
            self.device_info.describe = self.describeLineEdit.toPlainText()
            self.yesSignal.emit(self.device_info)
        else:
            InfoBar.error(
                title=self.tr('Error'),
                content=self.tr(err),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )

    def checkValid(self):
        if self.nameLineEdit.text() == "" : 
            return False, "name不能为空"
        if self.ipLineEdit.text() == "":
            return False, "ip不能为空"
        if re.match('^((?!00)\d{1,3}|0{0,2}\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])(\.((?!00)\d{1,3}|0{0,2}\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])){3}$', self.ipLineEdit.text()) == None:
            return False, "ip格式错误"
        return True, "Success"         

    def __setQss(self):
        self.nameLabel.setObjectName('nameLabel')
        self.ipLabel.setObjectName('ipLabel')
        self.describeLabel.setObjectName('describeLabel')        
        self.buttonGroup.setObjectName('buttonGroup')
        self.yesButton.setObjectName('yesButton')
        self.cancelButton.setObjectName('cancelButton')

        StyleSheet.DEVICE_DIALOG.apply(self)

        self.yesButton.adjustSize()
        self.cancelButton.adjustSize()


class Dialog(FramelessDialog, Ui_DeviceDialog):
    """ Dialog box """

    yesSignal = Signal(DeviceInfo)
    cancelSignal = Signal()

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(parent=parent)
        self._setUpUi(title, content, self)

        self.windowTitleLabel = QLabel(title, self)

        self.setResizeEnabled(False)
        self.resize(240, 192)
        self.titleBar.hide()

        self.vBoxLayout.insertWidget(0, self.windowTitleLabel, 0, Qt.AlignTop)
        self.windowTitleLabel.setObjectName('windowTitleLabel')
        StyleSheet.DEVICE_DIALOG.apply(self)
        self.setFixedSize(self.size())

    def setTitleBarVisible(self, isVisible: bool):
        self.windowTitleLabel.setVisible(isVisible)


class DeviceDialog(MaskDialogBase, Ui_DeviceDialog):
    """ Message box """

    yesSignal = Signal(DeviceInfo)
    cancelSignal = Signal()

    def __init__(self, device_info:DeviceInfo, parent = None):
        super().__init__(parent=parent)
        self._setUpUi(device_info, self.widget)

        self.setShadowEffect(60, (0, 10), QColor(0, 0, 0, 50))
        self.setMaskColor(QColor(0, 0, 0, 76))
        self._hBoxLayout.removeWidget(self.widget)
        self._hBoxLayout.addWidget(self.widget, 1, Qt.AlignCenter)

        self.buttonGroup.setMinimumWidth(280)
        # self.widget.setFixedSize(
        #     max(self.contentLabel.width(), self.titleLabel.width()) + 48,
        #     self.contentLabel.y() + self.contentLabel.height() + 105
        # )

    def eventFilter(self, obj, e: QEvent):
        if obj is self.window():
            if e.type() == QEvent.Resize:
                self._adjustText()

        return super().eventFilter(obj, e)
