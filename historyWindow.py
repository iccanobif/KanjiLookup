from PySide.QtCore import *
from PySide.QtGui import *
import re

class HistoryWindow(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.entries = set()
        
        self.lstHistory = QListWidget(self)
        self.lstHistory.setStyleSheet("font-size: 30px")
        layout = QHBoxLayout(self)
        layout.addWidget(self.lstHistory)
        self.setLayout(layout)

    def addEntry(self, entry):
        entry = re.sub("[0-9a-zA-Z]", "", entry).strip()
    
        if entry == "" or entry in self.entries: 
            return
        self.entries.add(entry)
        self.lstHistory.addItem(entry)
