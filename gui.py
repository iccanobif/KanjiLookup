from PySide.QtCore import *
from PySide.QtGui import *
import sys
import kanjidic
import lookup

kanjis = None

#TOFIX: se la finestra non è massimizzata e faccio doppio clic su "...", va in errore

def populateList(fullList):
    if kanjis == None: 
        return
    lstOutput.clear()
    if fullList:
        lstOutput.addItems(kanjis)
    else:
        lstOutput.addItems(kanjis[:100])
        if len(kanjis) > 100:
            lstOutput.addItem("...")
    if len(kanjis) > 0:
        lstOutput.itemAt(0, 0).setSelected(True)
        

def ontxtRadicalsInputChanged():
    global kanjis
    kanjis = lookup.getKanjiFromRadicals(txtRadicalsInput.text().replace("?", ",").split(","))
    # Sorting first by ord() value and then by stroke count, I ensure that kanji
    # with the same stoke count will always be ordered in a consistent way (by ord() value)
    kanjis = sorted(kanjis, key=ord)
    kanjis = sorted(kanjis, key=kanjidic.getStrokeCount)
    populateList(False)

def onlstOutputItemActivated(item):
    if item.text() == "...":
        populateList(True)
    else:
        txtOutputAggregation.insert(item.text())
        
def onbtnShowRadicalsClicked():
    radicals = lookup.getRadicalsFromKanji(txtOutputAggregation.text())
    text = ""
    for r in radicals:
        text += r + ": " + lookup.getRadicalName(r) + "<br/>"
    popup = Popup(window, text)
    popup.show()
    
class MainWindow(QWidget):
    def resizeEvent(self, event):
        populateList(False)
        
class Popup(QDialog):
    def __init__(self, parent, text):
        QDialog.__init__(self, parent)
        self.setWindowTitle("Radicals")
        self.setWindowModality(Qt.WindowModal)
        
        lblRadicals = QLabel(window)
        lblRadicals.setStyleSheet("font-size: 40px")
        lblRadicals.setText(text)
        layout = QHBoxLayout(self)
        layout.addWidget(lblRadicals)
        self.setLayout(layout)
        self.adjustSize()
    
app = QApplication(sys.argv)
window = MainWindow()
window.setWindowTitle("Kanji lookup")
window.resize(500, 600)
window.setStyleSheet("QListWidget {font-size: 70px}")
window.setWindowFlags(Qt.WindowStaysOnTopHint)

txtRadicalsInput = QLineEdit(window)
txtRadicalsInput.textChanged.connect(ontxtRadicalsInputChanged)

lstOutput = QListWidget(window)
lstOutput.setFlow(QListView.LeftToRight)
lstOutput.setWrapping(True)
lstOutput.itemActivated.connect(onlstOutputItemActivated)

txtOutputAggregation = QLineEdit(window)
txtOutputAggregation.setStyleSheet("font-size: 70px")

btnShowRadicals = QPushButton("Show radicals...", window)
btnShowRadicals.clicked.connect(onbtnShowRadicalsClicked)

#Layout

mainLayout = QVBoxLayout(window)
mainLayout.addWidget(txtRadicalsInput)
mainLayout.addWidget(lstOutput)

bottomLayout = QHBoxLayout()
bottomLayout.addWidget(txtOutputAggregation)
bottomLayout.addWidget(btnShowRadicals)

mainLayout.addLayout(bottomLayout)

window.show()
app.exec_()
