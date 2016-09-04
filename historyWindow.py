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
    
        if entry == "": # or entry in self.entries: 
            return
        self.entries.add(entry)
        
    def show(self):
        # newEntriesList = list(sorted(self.entries))
        # for i in range(0, len(newEntriesList)-1):
            # if len(list(filter(lambda x: x in i, newEntriesList[i:]))) == 0:
                # self.lstHistory.addItem(i)
        alreadyAdded = set()
        for i in self.entries:  
            if i in alreadyAdded:
                continue
            alreadyAdded.add(i)
            self.lstHistory.addItem(i)
        QDialog.show(self)
        
