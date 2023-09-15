from PySide6.QtGui import QIcon
from qfluentwidgets import LineEdit


class PasswordEdit(LineEdit):
    """
    A LineEdit with icons to show/hide password entries
    """
    CSS = """LineEdit {
        border-radius: 0px;
        height: 30px;
        margin: 0px 0px 0px 0px;
    }
    """

    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent)

        # Set styles
        #self.setStyleSheet(self.CSS)

        self.visibleIcon = QIcon(":/app/images/eye_on.png")
        self.hiddenIcon = QIcon(":/app/images/eye_off.png")

        self.setEchoMode(LineEdit.Password)
        self.togglepasswordAction = self.addAction(self.visibleIcon, LineEdit.TrailingPosition)
        self.togglepasswordAction.triggered.connect(self.on_toggle_password_Action)
        self.password_shown = False

    def on_toggle_password_Action(self):
        if not self.password_shown:
            self.setEchoMode(LineEdit.Normal)
            self.password_shown = True
            self.togglepasswordAction.setIcon(self.hiddenIcon)
        else:
            self.setEchoMode(LineEdit.Password)
            self.password_shown = False
            self.togglepasswordAction.setIcon(self.visibleIcon)