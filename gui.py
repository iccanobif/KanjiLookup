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

def ontxtKanjiInputChanged():
    lblRadicals.setText(lookup.getRadicalsFromKanji(txtKanjiInput.text()))
    
def onlstOutputItemActivated(item):
    if item.text() == "...":
        populateList(True)
    else:
        txtOutputAggregation.insert(item.text())
    
class MainWindow(QWidget):
    def resizeEvent(self, event):
        populateList(False)
    
app = QApplication(sys.argv)
window = MainWindow()
window.setWindowTitle("Kanji lookup")
window.resize(500, 600)
window.setStyleSheet("QListWidget {font-size: 70px}")

txtRadicalsInput = QLineEdit(window)
txtRadicalsInput.textChanged.connect(ontxtRadicalsInputChanged)

lstOutput = QListWidget(window)
lstOutput.setFlow(QListView.LeftToRight)
lstOutput.setWrapping(True)
lstOutput.itemActivated.connect(onlstOutputItemActivated)

txtOutputAggregation = QLineEdit(window)
txtOutputAggregation.setStyleSheet("font-size: 70px")

txtKanjiInput = QLineEdit(window)
txtKanjiInput.setStyleSheet("font-size: 40px")
txtKanjiInput.textChanged.connect(ontxtKanjiInputChanged)


lblRadicals = QLabel(window)
lblRadicals.setStyleSheet("font-size: 40px")
lblRadicals.setText("")

#Layout

mainLayout = QVBoxLayout(window)
mainLayout.addWidget(txtRadicalsInput)
mainLayout.addWidget(lstOutput)
mainLayout.addWidget(txtOutputAggregation)

shitLayout = QHBoxLayout()
shitLayout.addWidget(txtKanjiInput)
shitLayout.addWidget(lblRadicals)

mainLayout.addLayout(shitLayout)

window.show()
app.exec_()
