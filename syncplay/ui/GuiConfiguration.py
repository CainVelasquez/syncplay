from PySide import QtCore, QtGui
from PySide.QtCore import QSettings, Qt
from PySide.QtGui import QApplication, QLineEdit, QCursor, QLabel, QCheckBox

import os
import sys
from syncplay.messages import getMessage

class GuiConfiguration:
    def __init__(self, config):
        self.config = config
        self._availablePlayerPaths = []

    def run(self):
        self.app = QtGui.QApplication(sys.argv)
        dialog = ConfigDialog(self.config, self._availablePlayerPaths)
        dialog.exec_()

    def setAvailablePaths(self, paths):
        self._availablePlayerPaths = paths

    def getProcessedConfiguration(self):
        return self.config
    
    class WindowClosed(Exception):
        pass   

class ConfigDialog(QtGui.QDialog):
    
    pressedclosebutton = False
    
    malToggling = False
    
    def malToggled(self):
        if self.malToggling == False:
            self.malToggling = True
            
            if self.malenabledCheckbox.isChecked() and self.malenabledCheckbox.isVisible():
                self.malenabledCheckbox.setChecked(False)
                self.malSettingsGroup.setChecked(True)
                self.malSettingsGroup.show()
                self.malpasswordLabel.show()
                self.malpasswordTextbox.show()
                self.malusernameLabel.show()
                self.malusernameTextbox.show()
                self.malenabledCheckbox.hide()
            else:
                self.malSettingsGroup.setChecked(False)
                self.malSettingsGroup.hide()
                self.malpasswordLabel.hide()
                self.malpasswordTextbox.hide()
                self.malusernameLabel.hide()
                self.malusernameTextbox.hide()
                self.malenabledCheckbox.show()
                
            self.malToggling = False
            self.adjustSize()
            self.setFixedSize(self.sizeHint())
            
    def runButtonTextUpdate(self):
        if (self.donotstoreCheckbox.isChecked()):
            self.runButton.setText("Run Syncplay")
        else:
            self.runButton.setText("Store configuration and run Syncplay")

    def _tryToFillPlayerPath(self, playerpath, playerpathlist):
        foundpath = ""
        
        if playerpath != None and playerpath != "" and os.path.isfile(playerpath):
            foundpath = playerpath
            self.executablepathCombobox.addItem(foundpath)

        for path in playerpathlist:
            if(os.path.isfile(path) and path.lower() != foundpath.lower()):
                self.executablepathCombobox.addItem(path)
                if foundpath == None:
                    foundpath = path

        if foundpath:
            return(foundpath)
        else:
            return("")
    
    def browsePlayerpath(self):
        options = QtGui.QFileDialog.Options()
        defaultdirectory = ""
        browserfilter = "All Files (*)"
        
        if os.name == 'nt':
            browserfilter =  "Executable files (*.exe);;All Files (*)"
            if os.environ["ProgramFiles(x86)"] != "" and os.environ["ProgramFiles(x86)"] != None: 
                defaultdirectory = os.environ["ProgramFiles(x86)"]
            elif os.environ["ProgramFiles"] != os.environ["ProgramFiles"] != None:
                defaultdirectory = os.environ["ProgramFiles"]    
        elif sys.platform.startswith('linux'):
            defaultdirectory = "/usr/bin"
        
        fileName, filtr = QtGui.QFileDialog.getOpenFileName(self,
                "Browse for media player executable",
                defaultdirectory,
                browserfilter, "", options)
        if fileName:
            self.executablepathCombobox.setEditText(fileName)
        
    def _saveDataAndLeave(self):
        self.config['host'] = self.hostTextbox.text()
        self.config['name'] = self.usernameTextbox.text()
        self.config['room'] = self.defaultroomTextbox.text()
        self.config['password'] = self.serverpassTextbox.text()
        self.config['playerPath'] = self.executablepathCombobox.currentText()
        if self.alwaysshowCheckbox.isChecked() == True:
            self.config['forceGuiPrompt'] = True
        else:
            self.config['forceGuiPrompt'] = False
        if self.donotstoreCheckbox.isChecked() == True:
            self.config['noStore'] = True
        else:
            self.config['noStore'] = False
        if self.slowdownCheckbox.isChecked() == True:
            self.config['slowOnDesync'] = True
        else:
            self.config['slowOnDesync'] = False
        self.config['malUsername'] = self.malusernameTextbox.text()
        if self.malSettingsGroup.isChecked():
            self.config['malPassword'] = self.malpasswordTextbox.text()
        else:
            self.config['malPassword'] = ""
        self.pressedclosebutton = True
        self.close()
        return
    
    def closeEvent(self, event):
        if self.pressedclosebutton == False:
            sys.exit()
            raise GuiConfiguration.WindowClosed
            event.accept()
            
    def __init__(self, config, playerpaths):
        
        self.config = config

        super(ConfigDialog, self).__init__()
        
        self.setWindowTitle(getMessage("en", "config-window-title"))
              
        if(config['host'] == None):
            host = ""
        elif(":" in config['host']):
            host = config['host']
        else:
            host = config['host']+":"+str(config['port'])
            
        self.connectionSettingsGroup = QtGui.QGroupBox("Connection Settings")
        self.hostTextbox = QLineEdit(host, self)
        self.hostLabel = QLabel(getMessage("en", "host-label"), self)
        self.usernameTextbox = QLineEdit(config['name'],self)
        self.serverpassLabel = QLabel(getMessage("en", "password-label"), self)
        self.defaultroomTextbox = QLineEdit(config['room'],self)
        self.usernameLabel = QLabel(getMessage("en", "username-label"), self)
        self.serverpassTextbox = QLineEdit(config['password'],self)
        self.defaultroomLabel = QLabel(getMessage("en", "room-label"), self)
        self.connectionSettingsLayout = QtGui.QGridLayout()
        self.connectionSettingsLayout.addWidget(self.hostLabel, 0, 0)
        self.connectionSettingsLayout.addWidget(self.hostTextbox, 0, 1)
        self.connectionSettingsLayout.addWidget(self.serverpassLabel, 1, 0)
        self.connectionSettingsLayout.addWidget(self.serverpassTextbox, 1, 1)
        self.connectionSettingsLayout.addWidget(self.usernameLabel, 2, 0)
        self.connectionSettingsLayout.addWidget(self.usernameTextbox, 2, 1)
        self.connectionSettingsLayout.addWidget(self.defaultroomLabel, 3, 0)
        self.connectionSettingsLayout.addWidget(self.defaultroomTextbox, 3, 1)
        self.connectionSettingsGroup.setLayout(self.connectionSettingsLayout)
        
        self.mediaplayerSettingsGroup = QtGui.QGroupBox("Media Player Settings")
        self.executablepathCombobox = QtGui.QComboBox(self)
        self.executablepathCombobox.setEditable(True)
        self.executablepathCombobox.setEditText(self._tryToFillPlayerPath(config['playerPath'],playerpaths))
        self.executablepathCombobox.setMinimumWidth(200)
        self.executablepathCombobox.setMaximumWidth(200)
        self.executablepathLabel = QLabel("Path to player executable:", self)
        self.executablebrowseButton = QtGui.QPushButton("Browse")
        self.executablebrowseButton.clicked.connect(self.browsePlayerpath)
        self.slowdownCheckbox = QCheckBox("Slow down on desync")
        self.mediaplayerSettingsLayout = QtGui.QGridLayout()
        self.mediaplayerSettingsLayout.addWidget(self.executablepathLabel, 0, 0)
        self.mediaplayerSettingsLayout.addWidget(self.executablepathCombobox , 0, 1)
        self.mediaplayerSettingsLayout.addWidget(self.executablebrowseButton , 0, 2)
        self.mediaplayerSettingsLayout.addWidget(self.slowdownCheckbox, 1, 0)
        self.mediaplayerSettingsGroup.setLayout(self.mediaplayerSettingsLayout)
        if config['slowOnDesync'] == True:
            self.slowdownCheckbox.setChecked(True)

        self.malSettingsGroup = QtGui.QGroupBox("Enable MyAnimeList Updater (EXPERIMENTAL)")
        self.malSettingsGroup.setCheckable(True)
        self.malSettingsGroup.toggled.connect(self.malToggled)
        self.malSettingsSplit = QtGui.QSplitter(self)
        self.malusernameTextbox = QLineEdit(config['malUsername'],self)
        self.malusernameLabel = QLabel("MAL Username:", self)
        self.malpasswordTextbox = QLineEdit(config['malPassword'],self)
        self.malpasswordTextbox.setEchoMode(QtGui.QLineEdit.Password)
        self.malpasswordLabel = QLabel("MAL Password:", self)
        self.malSettingsLayout = QtGui.QGridLayout()
        self.malSettingsLayout.addWidget(self.malusernameLabel , 0, 0)
        self.malSettingsLayout.addWidget(self.malusernameTextbox, 0, 1)
        self.malSettingsLayout.addWidget(self.malpasswordLabel , 1, 0)
        self.malSettingsLayout.addWidget(self.malpasswordTextbox, 1, 1)
        self.malSettingsGroup.setLayout(self.malSettingsLayout)
        
        self.malenabledCheckbox = QCheckBox("Enable MyAnimeList Updater (EXPERIMENTAL)")
        self.malenabledCheckbox.toggled.connect(self.malToggled) 
        if config['malPassword'] == None or config['malPassword'] == "":
            self.malenabledCheckbox.setChecked(False)
            self.malSettingsGroup.hide()
        else:
            self.malenabledCheckbox.hide()
        
        self.alwaysshowCheckbox = QCheckBox("Always Show This Dialog")
        if config['forceGuiPrompt'] == True:
            self.alwaysshowCheckbox.setChecked(True)
        
        self.donotstoreCheckbox = QCheckBox("Do Not Store This Configuration")
        if config['noStore'] == True:
            self.donotstoreCheckbox.setChecked(True)
        
        self.runButton = QtGui.QPushButton("Store configuration and run Syncplay")
        self.runButton.pressed.connect(self._saveDataAndLeave)
        self.runButtonTextUpdate
        self.donotstoreCheckbox.toggled.connect(self.runButtonTextUpdate)
                      
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.addWidget(self.connectionSettingsGroup)
        self.mainLayout.addSpacing(12)
        self.mainLayout.addWidget(self.mediaplayerSettingsGroup)
        self.mainLayout.addSpacing(12)
        self.mainLayout.addWidget(self.malenabledCheckbox)
        self.mainLayout.addWidget(self.malSettingsGroup)
        
        self.mainLayout.addWidget(self.alwaysshowCheckbox)
        self.mainLayout.addWidget(self.donotstoreCheckbox)
        self.mainLayout.addWidget(self.runButton)
        
        self.mainLayout.addStretch(1)
        
        self.setLayout(self.mainLayout)
        self.setFixedSize(self.sizeHint())
