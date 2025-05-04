import minecraft_launcher_lib

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QSize, Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QComboBox, QSpacerItem, QSizePolicy, QProgressBar, QPushButton, QApplication, QMainWindow
from PyQt5.QtGui import QPixmap

from minecraft_launcher_lib.utils import get_minecraft_directory, get_version_list
from minecraft_launcher_lib.install import install_minecraft_version
from minecraft_launcher_lib.command import get_minecraft_command
from minecraft_launcher_lib import *

from random_username.generate import generate_username
from uuid import uuid1

from subprocess import call
from sys import argv, exit

minecraft_directory = get_minecraft_directory().replace('minecraft', 'zowalauncher')

class LaunchThread(QThread):
    launch_setup_signal = pyqtSignal(str, str)
    progress_update_signal = pyqtSignal(int, int, str)
    state_update_signal = pyqtSignal(bool)

    version_id = ''
    username = ''

    progress = 0
    progress_max = 0
    progress_label = ''

    def __init__(self):
        super().__init__()
        self.launch_setup_signal.connect(self.launch_setup)
    
    def launch_setup(self, version_id, username):
        self.version_id = version_id
        self.username = username
    
    def update_progress_label(self, value):
        self.progress_label = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)
    def update_progress(self, value):
        self.progress = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)
    def update_progress_max(self, value):
        self.progress_max = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)
    
    def run(self):
        self.state_update_signal.emit(True)

        install_minecraft_version(versionid=self.version_id, minecraft_directory=minecraft_directory, callback={ 'setStatus': self.update_progress_label, 'setProgress': self.update_progress, 'setMax': self.update_progress_max})

        if self.username == '':
            self.username = generate_username()[0]
        
        options = {
            'username': self.username,
            'uuid': str(uuid1()),
            'token': ''
        }

        call(get_minecraft_command(version=self.version_id, minecraft_directory=minecraft_directory, options=options))
        self.state_update_signal.emit(False)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(502, 384)
        MainWindow.setMaximumSize(QtCore.QSize(2067, 393))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.Username = QtWidgets.QLineEdit(self.centralwidget)
        self.Username.setObjectName("Username")
        self.Username.setPlaceholderText('Username')
        self.verticalLayout.addWidget(self.Username)
        self.version_select = QtWidgets.QComboBox(self.centralwidget)
        self.version_select.setObjectName("version_select")
        
        for version in get_version_list():
            self.version_select.addItem(version['id'])
        
        self.verticalLayout.addWidget(self.version_select)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.verticalLayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setEnabled(True)
        self.label.setMaximumSize(QtCore.QSize(16777215, 16777197))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("assets/model2.png"))
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem1)
        self.start_progress = QtWidgets.QProgressBar(self.centralwidget)
        self.start_progress.setProperty("value", 24)
        self.start_progress.setVisible(False)
        self.start_progress.setObjectName("start_progress")
        self.verticalLayout.addWidget(self.start_progress)
        self.start_button = QtWidgets.QPushButton(self.centralwidget)
        self.start_button.setMaximumSize(QtCore.QSize(16777198, 16777215))
        icon = QtGui.QIcon.fromTheme("ччве")
        self.start_button.setIcon(icon)
        self.start_button.setObjectName("start_button")
        self.start_button.setText("Играть")
        self.start_button.clicked.connect(self.launch_game)
        self.verticalLayout.addWidget(self.start_button)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)

        self.launch_thread = LaunchThread()
        self.launch_thread.state_update_signal.connect(self.state_update)
        self.launch_thread.progress_update_signal.connect(self.update_progress)

    def state_update(self, value):
        self.start_button.setDisabled(value)
        self.start_progress.setVisible(value)
    def update_progress(self, progress, max_progress, label):
        self.start_progress.setValue(progress)
        self.start_progress.setMaximum(max_progress)
    def launch_game(self):
        self.launch_thread.launch_setup_signal.emit(self.version_select.currentText(), self.Username.text())
        self.launch_thread.start()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
