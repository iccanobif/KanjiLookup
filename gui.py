from PySide.QtCore import *
from PySide.QtGui import *
import sys
import kanjidic
import lookup
import edict

#TOFIX: non funziona "show radicals" per 就


#TOFIX: se la finestra non è massimizzata e faccio doppio clic su "...", va in errore

def populateList(fullList):
    kanjis = lookup.getKanjiFromRadicals(txtRadicalsInput.text().replace("?", ",").split(","))
    # Sorting first by ord() value and then by stroke count, I ensure that kanji
    # with the same stoke count will always be ordered in a consistent way (by ord() value)
    kanjis = sorted(kanjis, key=ord)
    kanjis = sorted(kanjis, key=kanjidic.getStrokeCount)
    
    if spnStrokeCount.value() > 0:
        kanjis = list(filter(lambda x: kanjidic.getStrokeCount(x) == spnStrokeCount.value(), kanjis))
    
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
    populateList(False)

def onlstOutputItemActivated(item):
    if item.text() == "...":
        populateList(True)
    else:
        txtOutputAggregation.insert(item.text())
        
def onbtnShowRadicalsClicked():
    text = ""
    for k in txtOutputAggregation.text():
        radicals = lookup.getRadicalsFromKanji(k)
        if len(radicals) == 0: continue
        
        if text != "": text += "<br/>"
        text += k + ":<br/>"
        
        for r in radicals:
            text += "    " + r + ": " + lookup.getRadicalName(r) + "<br/>"

    popup = Popup(window, text)
    popup.show()
    
def onbtnShowTranslationClicked():
    text = ""
    
    translations = edict.getTranslation(txtOutputAggregation.text())
    
    if translations is None:
        text = "-- not found --"
        
    for t in translations:
        text += t + "\n"
    
    popup = Popup(window, text.strip())
    popup.show()
    
def onspnStrokeCountValueChanged(value):
    populateList(False)
    
class MainWindow(QWidget):
    def resizeEvent(self, event):
        populateList(False)
        
class Popup(QDialog):
    def __init__(self, parent, text):
        QDialog.__init__(self, parent)
        self.setWindowModality(Qt.WindowModal)
        
        label = QLabel(window)
        label.setStyleSheet("font-size: 40px")
        label.setWordWrap(True)
        label.setText(text)
        layout = QHBoxLayout(self)
        layout.addWidget(label)
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

btnShowTranslation = QPushButton("Show translation...", window)
btnShowTranslation.clicked.connect(onbtnShowTranslationClicked)

lblStrokeCount = QLabel("Stroke count:")
spnStrokeCount = QSpinBox(window)
spnStrokeCount.valueChanged.connect(onspnStrokeCountValueChanged)

#Layout

mainLayout = QVBoxLayout(window)
mainLayout.addWidget(txtRadicalsInput)
mainLayout.addWidget(lstOutput)

bottomLayout = QHBoxLayout()
bottomLayout.addWidget(txtOutputAggregation)
buttonsLayout = QVBoxLayout()
buttonsLayout.addWidget(btnShowRadicals)
buttonsLayout.addWidget(btnShowTranslation)
bottomLayout.addLayout(buttonsLayout)

mainLayout.addLayout(bottomLayout)

strokeCountLayout = QHBoxLayout()
strokeCountLayout.addWidget(lblStrokeCount)
strokeCountLayout.addWidget(spnStrokeCount)
mainLayout.addLayout(strokeCountLayout)
lblStrokeCount.adjustSize()

window.show()
app.exec_()
