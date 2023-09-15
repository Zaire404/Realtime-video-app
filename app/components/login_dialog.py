# coding:utf-8
from PySide6.QtCore import Qt, Signal, QObject, QEvent
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit
from qframelesswindow import FramelessDialog

from qfluentwidgets import TextWrap, PrimaryPushButton, LineEdit
from qfluentwidgets.components.dialog_box.mask_dialog_base import MaskDialogBase

from ..components.password_edit import PasswordEdit
from ..common.style_sheet import StyleSheet

# device_name  device_ip describe
class Ui_LoginDialog:
    """ Ui of login dialog """

    loginSignal = Signal()
    registerSignal = Signal()

    def __init__(self, *args, **kwargs):
        pass

    def _setUpUi(self, parent = None):
        self.accountLabel = QLabel('Account', parent)
        self.passwordLabel = QLabel('Password', parent)
        self.accountLineEdit = LineEdit(self)
        self.passwordLineEdit = PasswordEdit(self)
        
        self.buttonGroup = QFrame(parent)
        self.loginButton = PrimaryPushButton(self.tr('Login'), self.buttonGroup)
        self.registerButton = QPushButton(self.tr('Register'), self.buttonGroup)

        self.vBoxLayout = QVBoxLayout(parent)
        self.contentLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout(self.buttonGroup)

        self.__initWidget()

    def __initWidget(self):
        self.passwordLineEdit.setEchoMode(QLineEdit.Password)
        self.__setQss()
        self.__initLayout()

        self.loginButton.setAttribute(Qt.WA_LayoutUsesWidgetRect)
        self.registerButton.setAttribute(Qt.WA_LayoutUsesWidgetRect)

        self.loginButton.setFocus()
        self.buttonGroup.setFixedHeight(81)

        self.loginButton.clicked.connect(self.__onLoginButtonClicked)
        self.registerButton.clicked.connect(self.__onRegisterButtonClicked)


    def __initLayout(self):
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addLayout(self.contentLayout, 1)
        self.vBoxLayout.addWidget(self.buttonGroup, 0, Qt.AlignBottom)
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)

        self.contentLayout.setSpacing(12)
        self.contentLayout.setContentsMargins(24, 24, 24, 24)   
        self.contentLayout.addWidget(self.accountLabel)
        self.contentLayout.addWidget(self.accountLineEdit)
        self.contentLayout.addWidget(self.passwordLabel)
        self.contentLayout.addWidget(self.passwordLineEdit)
                
        self.buttonLayout.setSpacing(12)
        self.buttonLayout.setContentsMargins(24, 24, 24, 24)
        self.buttonLayout.addWidget(self.loginButton, 1, Qt.AlignVCenter)
        self.buttonLayout.addWidget(self.registerButton, 1, Qt.AlignVCenter)

    def __onRegisterButtonClicked(self):
        self.reject()
        self.cancelSignal.emit()

    def __onLoginButtonClicked(self):
        self.accept()
        self.yesSignal.emit()

    def __setQss(self):
        self.accountLabel.setObjectName('accountLabel')
        self.passwordLabel.setObjectName('passwordLabel')
        self.buttonGroup.setObjectName('buttonGroup')
        self.loginButton.setObjectName('loginButton')
        self.registerButton.setObjectName('registerButton')

        StyleSheet.LOGIN_DIALOG.apply(self)

        self.loginButton.adjustSize()
        self.registerButton.adjustSize()
        
        


class Dialog(FramelessDialog, Ui_LoginDialog):
    loginSignal = Signal()
    registerSignal = Signal()

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(parent=parent)
        self._setUpUi(title, content, self)

        self.windowTitleLabel = QLabel(title, self)

        self.setResizeEnabled(False)
        self.resize(240, 192)
        self.titleBar.hide()

        self.vBoxLayout.insertWidget(0, self.windowTitleLabel, 0, Qt.AlignTop)
        self.windowTitleLabel.setObjectName('windowTitleLabel')
        StyleSheet.LOGIN_DIALOG.apply(self)
        self.setFixedSize(self.size())

    def setTitleBarVisible(self, isVisible: bool):
        self.windowTitleLabel.setVisible(isVisible)


class LoginDialog(MaskDialogBase, Ui_LoginDialog):
    loginSignal = Signal()
    registerSignal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._setUpUi(self.widget)

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
