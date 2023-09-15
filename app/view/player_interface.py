from qfluentwidgets import ScrollArea, ToggleButton, ComboBox, InfoBar, InfoBarPosition
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout,QLabel
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QApplication
from ..components.device_info import DeviceInfo
from ..common.style_sheet import StyleSheet
from ..thread.capture_thread import CaptureThread
from ..thread.command_thread import CommandThread

class PlayerInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.openThreadText = "Start Thread"
        self.closeThreadText = "Close Thread"
        self.current_pixmap = None
        self.titleLabel = QLabel('Player', self)
        self.imageScene = QGraphicsScene()
        self.imageView = QGraphicsView(self)
        self.player_hBoxLayout = QHBoxLayout()
        self.control_vboxLayout = QVBoxLayout()
        self.vBoxLayout = QVBoxLayout(self)
        self.playButton = ToggleButton(self.openThreadText, self)
        self.comboBox = ComboBox()
        
        self.titleLabel.setObjectName('titleLabel')
        self.imageView.setObjectName('imageView')
        
        self.__initLayout()
        self.__initWidget()
        
    def __initWidget(self):
        StyleSheet.DEVICE_CARD.apply(self)
        self.imageView.setFixedHeight(722)
        self.imageView.setFixedWidth(1280)
        # self.imageView.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.imageView.setScene(self.imageScene)
        self.imageView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.imageView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.comboBox.setFixedSize(150, 40)
        self.playButton.setFixedSize(150, 45)   
        self.playButton.clicked.connect(self.on_playButton_clicked)
        self.comboBox.currentIndexChanged.connect(self.comboBoxCurrentIndexChanged)
        
        StyleSheet.PLAYER_INTERFACE.apply(self)
        # self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # self.titleLabel.setFont(QFont("Microsoft YaHei", 20, 75))
        
    def __initLayout(self):
        self.control_vboxLayout.addStretch(1)
        self.control_vboxLayout.addWidget(self.comboBox)
        self.control_vboxLayout.addStretch(1)
        self.control_vboxLayout.addWidget(self.playButton)
        self.control_vboxLayout.addStretch(1)
        
        self.player_hBoxLayout.addWidget(self.imageView)
        self.player_hBoxLayout.addStretch(1)
        self.player_hBoxLayout.addLayout(self.control_vboxLayout)
        self.player_hBoxLayout.addStretch(1)
        self.vBoxLayout.setContentsMargins(36, 0, 36, 0)
        self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addLayout(self.player_hBoxLayout)
        self.vBoxLayout.addStretch(1)
        
    @Slot(DeviceInfo)
    def addDeviceComboItem(self, device_info: DeviceInfo):
        self.comboBox.addItem(text = device_info.name + "(" + device_info.ip + ")", userData = device_info.ip)
    
    @Slot(int)
    def comboBoxCurrentIndexChanged(self, int):
        QApplication.processEvents()
        self.cleanupThreads()
        self.connectServer(self.comboBox.currentData())
        self.playButton._postInit()
    
    
    def on_playButton_clicked(self):
        print(self.playButton.isChecked())
        print(self.comboBox.currentIndex())
        if self.comboBox.currentIndex() == -1:
            self.showErrorMessage("未选择设备!")
            self.playButton._postInit()
            return

        if self.commandThread.isConnect() != True:
            self.showErrorMessage("未连接到设备!")
            self.playButton._postInit()
            return 
        
        if self.playButton.isChecked() :
            self.playButton.setText(self.closeThreadText)
            self.commandThread.send_command("Start")            
        else:
            self.playButton.setText(self.openThreadText)
            self.commandThread.send_command("Stop")
            
    def connectServer(self, ip):
        self.captureThread = CaptureThread()
        self.captureThread.signal_image.connect(self.showImage)
        self.captureThread.errorSignal.connect(self.showErrorMessage)
        self.captureThread.InitPort(ip, 15006)
        self.captureThread.InitSocket()
        self.captureThread.Threadopen = True
        self.captureThread.start()
        
        self.commandThread = CommandThread()
        self.commandThread.errorSignal.connect(self.showErrorMessage)
        self.commandThread.InitPort(ip, 15005)
        self.commandThread.InitSocket()
        self.commandThread.Threadopen = True
        self.commandThread.start()
        
        
    def cleanupThreads(self):
        if hasattr(self, 'captureThread') and self.captureThread:
            # self.captureThread.stop()
            self.captureThread.wait()
            self.captureThread = None

        if hasattr(self, 'commandThread') and self.commandThread:
            # self.commandThread.stop()
            self.commandThread.wait()
            self.commandThread = None
            
            
    def showImage(self, image):
        if self.current_pixmap is not None:
            self.current_pixmap = None  # Release the old QPixmap
        self.current_pixmap = image
        self.imageScene.clear()
        self.imageScene.addPixmap(self.current_pixmap)
        
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
        
    def closeEvent(self, event):
        if self.current_pixmap is not None:
            self.current_pixmap = None  # Release the QPixmap when closing the window
        self.captureThread.Threadopen = False
        self.commandThread.Threadopen = False
        self.cleanupThreads()
        event.accept()