from PySide.QtCore import *
from PySide.QtGui import *
import utf8console
import sys
import kanjidic
import lookup

def kanjiCompare(k):
    strokes = kanjidic.getStrokeCount(k)
    return strokes * 1000000 + ord(k)

def ontxtRadicalsInputChanged():
    kanjis = lookup.getKanjiFromRadicals(txtRadicalsInput.text().replace("?", ",").split(","))
    #kanjis = sorted(kanjis, key=kanjidic.getStrokeCount)
    kanjis = sorted(kanjis, key=kanjiCompare)
    lstOutput.clear()
    lstOutput.addItems(kanjis[:100])
    if len(kanjis) > 0:
        lstOutput.itemAt(0, 0).setSelected(True)
        if len(kanjis) > 100:
            lstOutput.addItem("...")

def ontxtKanjiInputChanged():
    lblRadicals.setText(lookup.getRadicalsFromKanji(txtKanjiInput.text()))
    
def onlstOutputItemActivated(item):
    txtOutputAggregation.insert(item.text())

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Kanji lookup")
window.resize(500, 600)
window.setStyleSheet("QListWidget, QLineEdit#txtOutputAggregation {font-size: 70px}")

txtRadicalsInput = QLineEdit(window)
txtRadicalsInput.textChanged.connect(ontxtRadicalsInputChanged)

lstOutput = QListWidget(window)
lstOutput.setFlow(QListView.LeftToRight)
lstOutput.setWrapping(True)
lstOutput.itemActivated.connect(onlstOutputItemActivated)

txtOutputAggregation = QLineEdit(window)
txtOutputAggregation.setStyleSheet("font-size: 70px")

txtKanjiInput = QLineEdit(window)
txtKanjiInput.textChanged.connect(ontxtKanjiInputChanged)

lblRadicals = QLabel(window)

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
