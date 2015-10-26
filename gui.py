from PySide.QtCore import *
from PySide.QtGui import *
import utf8console
import romkan
import sys
import kanjidic
import lookup
import edict
from historyWindow import HistoryWindow

def populateList(fullList):
    kanjis = lookup.getKanjiFromRadicals(txtRadicalsInput.text().lower().replace("、", ",").split(","))
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
        lstOutput.item(0).setSelected(True)
        lstOutput.scrollToTop()

def ontxtRadicalsTextChanged():
    populateList(False)

def onlstOutputItemActivated(item):
    if item.text() == "...":
        populateList(True)
    else:
        if (QApplication.keyboardModifiers() & Qt.ShiftModifier) == Qt.ShiftModifier:
            txtOutputAggregation.setText("")
        txtOutputAggregation.insert(item.text())
        
def onbtnShowRadicalsClicked():
    text = ""
    for k in txtOutputAggregation.text():
        radicals = lookup.getRadicalsFromKanji(k)
        if len(radicals) == 0: continue
        
        if text != "": text += "<br/>"
        text += k + ":<br/>"
        
        for r in radicals:
            text += r + ": " + lookup.getRadicalName(r) + "<br/>"

    popup = Popup(window, text)
    popup.show()
    
def getTranslations():
    text = ""
    
    translations = edict.getTranslation(romkan.to_hiragana(txtOutputAggregation.text().replace(" ", "")))
    
    if translations is None:
        text = "-- not found --"
    else:
        for t in translations:
            if text != "": text += "--------\n"
            text += t + "\n"
    return text.strip()

def onbtnShowTranslationClicked():
    popup = Popup(window, getTranslations())
    popup.show()
    
def onbtnShowHistoryClicked():
    historyWindow.show()
    
def onspnStrokeCountValueChanged(value):
    populateList(False)
    
def onbtnSplitClicked():
    text = ""
    for w in edict.splitSentence(txtOutputAggregation.text()):
        text += w + "/"
    popup = Popup(window, text.strip("/"))
    popup.show()
    
def ontxtOutputAggregationTextChanged():
    historyWindow.addEntry(txtOutputAggregation.text())
    txtTranslations.setPlainText(getTranslations())
    
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
# window.setStyleSheet("QListWidget {font-size: 70px}")
window.setWindowFlags(Qt.WindowStaysOnTopHint)

historyWindow = HistoryWindow(window)

txtRadicalsInput = QLineEdit(window)
txtRadicalsInput.textChanged.connect(ontxtRadicalsTextChanged)

lstOutput = QListWidget(window)
lstOutput.setFlow(QListView.LeftToRight)
lstOutput.setWrapping(True)
lstOutput.itemActivated.connect(onlstOutputItemActivated)
lstOutput.setStyleSheet("QListWidget {font-size: 70px}")

txtOutputAggregation = QLineEdit(window)
txtOutputAggregation.setStyleSheet("font-size: 70px")
txtOutputAggregation.textChanged.connect(ontxtOutputAggregationTextChanged)

btnShowTranslation = QPushButton("Show translation...", window)
btnShowTranslation.clicked.connect(onbtnShowTranslationClicked)
btnShowTranslation.setVisible(False)

btnShowRadicals = QPushButton("Show radicals...", window)
btnShowRadicals.clicked.connect(onbtnShowRadicalsClicked)

btnShowHistory = QPushButton("History...", window)
btnShowHistory.clicked.connect(onbtnShowHistoryClicked)

btnSplit = QPushButton("Split...", window)
btnSplit.clicked.connect(onbtnSplitClicked)

txtTranslations = QTextEdit(window)
txtTranslations.setReadOnly(True)
txtTranslations.setStyleSheet("font-size: 25px")

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
buttonsLayout.addWidget(btnShowTranslation)
buttonsLayout.addWidget(btnShowRadicals)
buttonsLayout.addWidget(btnShowHistory)
buttonsLayout.addWidget(btnSplit)
bottomLayout.addLayout(buttonsLayout)

mainLayout.addLayout(bottomLayout)

mainLayout.addWidget(txtTranslations)

strokeCountLayout = QHBoxLayout()
strokeCountLayout.addWidget(lblStrokeCount)
strokeCountLayout.addWidget(spnStrokeCount)
mainLayout.addLayout(strokeCountLayout)
lblStrokeCount.adjustSize()

window.show()
app.exec_()
