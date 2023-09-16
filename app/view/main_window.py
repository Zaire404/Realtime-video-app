# coding: utf-8
from PySide6.QtCore import Qt, Signal, QEasingCurve
from PySide6.QtWidgets import QApplication, QHBoxLayout, QFrame, QWidget

from qfluentwidgets import (
    NavigationInterface,
    NavigationItemPosition,
    PopUpAniStackedWidget,
    qrouter,
)
from qfluentwidgets import FluentIcon as FIF
from app.components.frameless_window import FramelessWindow
from app.components.avatar_widget import AvatarWidget
from app.components.login_dialog import LoginDialog
from app.common.style_sheet import StyleSheet
from app.common import resource
from app.view.title_bar import CustomTitleBar
from app.view.home_interface import HomeInterface
from app.view.device_interface import DeviceInterface
from app.view.player_interface import PlayerInterface


class StackedWidget(QFrame):
    currentWidgetChanged = Signal(QWidget)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.view = PopUpAniStackedWidget(self)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.view)
        self.view.currentChanged.connect(
            lambda x: self.currentWidgetChanged.emit(self.view.widget(x))
        )

    def addWidget(self, widget):
        self.view.addWidget(widget)

    def setCurrentWidget(self, widget, popOut=True):
        widget.verticalScrollBar().setValue(0)
        if not popOut:
            self.view.setCurrentWidget(widget, duration=300)
        else:
            self.view.setCurrentWidget(
                widget, True, False, 300, QEasingCurve.Type.InQuad
            )

    def setCurrentIndex(self, index, popOut=False):
        self.setCurrentWidget(self.view.widget(index), popOut)


class MainWindow(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.setTitleBar(CustomTitleBar(self))
        self.hBoxLayout = QHBoxLayout(self)
        self.widgetLayout = QHBoxLayout()
        self.stackWidget = StackedWidget(self)
        self.navigation = NavigationInterface(self, True, True)

        self.homeInterface = HomeInterface(self)
        self.deviceInterface = DeviceInterface(self)
        self.playerInterface = PlayerInterface(self)

        self.deviceInterface.deviceCardView.deviceAdded.connect(
            self.playerInterface.addDeviceComboItem
        )

        self.initLayout()
        self.initNavigation()
        self.initWindow()

    def initWindow(self):
        self.resize(1920, 1080)
        self.setWindowTitle("Testtest")
        self.titleBar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

        # 窗口居中
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        StyleSheet.MAIN_WINDOW.apply(self)

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.navigation)
        self.hBoxLayout.addLayout(self.widgetLayout)
        self.hBoxLayout.setStretchFactor(self.widgetLayout, 1)

        self.widgetLayout.addWidget(self.stackWidget)
        self.widgetLayout.setContentsMargins(0, 48, 0, 0)

        self.titleBar.raise_()
        self.navigation.displayModeChanged.connect(self.titleBar.raise_)

    def switchTo(self, widget, triggerByUser=True):
        self.stackWidget.setCurrentWidget(widget, not triggerByUser)

    def addSubInterface(
        self,
        interface: QWidget,
        objectName: str,
        icon,
        text: str,
        position=NavigationItemPosition.SCROLL,
    ):
        interface.setObjectName(objectName)
        self.stackWidget.addWidget(interface)
        self.navigation.addItem(
            routeKey=objectName,
            icon=icon,
            text=text,
            onClick=lambda t: self.switchTo(interface, t),
            position=position,
            tooltip=text,
        )

    def onCurrentWidgetChanged(self, widget: QWidget):
        self.navigation.setCurrentItem(widget.objectName())
        qrouter.push(self.stackWidget, widget.objectName())

    def resizeEvent(self, e):
        self.titleBar.move(46, 0)
        self.titleBar.resize(self.width() - 46, self.titleBar.height())

    def initNavigation(self):
        self.addSubInterface(
            self.homeInterface,
            "homeInterface",
            FIF.HOME,
            self.tr("Home"),
            NavigationItemPosition.TOP,
        )
        self.addSubInterface(
            self.deviceInterface,
            "deviceInterface",
            FIF.ADD,
            self.tr("Device"),
            NavigationItemPosition.TOP,
        )
        self.addSubInterface(
            self.playerInterface,
            "PlayerInterface",
            FIF.MOVIE,
            self.tr("Player"),
            NavigationItemPosition.TOP,
        )

        self.navigation.addWidget(
            routeKey="avatar",
            widget=AvatarWidget(":/app/images/user.png"),
            onClick=self.login,
            position=NavigationItemPosition.BOTTOM,
        )

        qrouter.setDefaultRouteKey(self.stackWidget, self.homeInterface.objectName())

        self.stackWidget.currentWidgetChanged.connect(self.onCurrentWidgetChanged)
        self.navigation.setCurrentItem(self.homeInterface.objectName())
        self.stackWidget.setCurrentIndex(0)

    def login(self):
        print("login")
        w = LoginDialog(parent=self.window())
        if w.exec():
            print("login")
        else:
            print("register")
