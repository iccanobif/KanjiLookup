import sys
import os
if sys.executable.endswith("pythonw.exe"):
    sys.stderr = open(os.devnull, "w")

from PySide.QtCore import *
from PySide.QtGui import *

app = QApplication(sys.argv)
pixmap = QPixmap("splash.png")
splashScreen = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
splashScreen.show()
app.processEvents()

# import utf8console
import romkan
splashScreen.showMessage("Loading kanjidic...")
import kanjidic
splashScreen.showMessage("Loading kradfile...")
import lookup
splashScreen.showMessage("Loading edict...")
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
    
def showTranslations(word):
    translations = edict.getTranslation(word)
    
    if translations is None:
        txtTranslations.setPlainText("-- not found --")
    else:
        txtTranslations.setPlainText("\n--------\n".join(translations))

def onbtnShowHistoryClicked():
    historyWindow.show()
    
def onspnStrokeCountValueChanged(value):
    populateList(False)
    
def onbtnSearchWordClicked():
    popup = ListPopup(window)
    popup.show(edict.findWordsFromFragment(txtOutputAggregation.text()))
    
    
def ontxtOutputAggregationTextChanged():
    historyWindow.addEntry(txtOutputAggregation.text())
    
    input = txtOutputAggregation.text()
    
    if input == "":
        txtTranslations.setPlainText("")
        lblSplittedWordsList.setText("")
        return
    
    words = edict.splitSentence(input)
    
    showTranslations(words[0])
    
    text = ""
    for w in words:
        text += "<a href='word'>word</a> ".replace("word", w)
    lblSplittedWordsList.setText(text)
    
def ontxtOutputAggregationSelectionChanged():
    if txtOutputAggregation.hasSelectedText():
        showTranslations(txtOutputAggregation.selectedText())
    else:
        showTranslations(txtOutputAggregation.text())

def ontxtOutputAggregationCursorPositionChanged(oldPosition, newPosition):
    if txtOutputAggregation.hasSelectedText(): 
        return # Let ontxtOutputAggregationSelectionChanged() handle this
    
    # This stuff doesn't work: the input text (possibly in romaji) doesn't necessarily have
    # the same length as what splitSentence() spits out...
    # i = 0
    # for w in edict.splitSentence(txtOutputAggregation.text()):
        # if len(w) + i > newPosition:
            # showTranslations(w)
            # return
    
def onlblSplittedWordsListlinkActivated(link):
    showTranslations(link)
    
class MainWindow(QWidget):
    def resizeEvent(self, event):
        populateList(False)
        
class Popup(QDialog):
    def __init__(self, parent, text):
        QDialog.__init__(self, parent)
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle("Kanji lookup")
        
        label = QLabel(window)
        label.setStyleSheet("font-size: 40px")
        label.setWordWrap(True)
        label.setText(text)
        layout = QHBoxLayout(self)
        layout.addWidget(label)
        self.setLayout(layout)
        self.adjustSize()
        
class ListPopup(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.entries = set()
        
        self.list = QListWidget(self)
        self.list.setStyleSheet("font-size: 30px")
        layout = QHBoxLayout(self)
        layout.addWidget(self.list)
        self.setLayout(layout)
        
    def show(self, items):
        for i in items:
            self.list.addItem(i)
        QDialog.show(self)
        
window = MainWindow()
window.setWindowTitle("Kanji lookup")
window.resize(500, 600)
window.setWindowFlags(Qt.WindowStaysOnTopHint)
window.setWindowIcon(QIcon("icon.png"))

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
txtOutputAggregation.selectionChanged.connect(ontxtOutputAggregationSelectionChanged)
txtOutputAggregation.cursorPositionChanged.connect(ontxtOutputAggregationCursorPositionChanged)

btnShowRadicals = QPushButton("Show radicals...", window)
btnShowRadicals.clicked.connect(onbtnShowRadicalsClicked)

btnShowHistory = QPushButton("History...", window)
btnShowHistory.clicked.connect(onbtnShowHistoryClicked)

btnSearchWord = QPushButton("Search...", window)
btnSearchWord.clicked.connect(onbtnSearchWordClicked)

lblSplittedWordsList = QLabel(window)
lblSplittedWordsList.linkActivated.connect(onlblSplittedWordsListlinkActivated)

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
buttonsLayout.addWidget(btnShowRadicals)
buttonsLayout.addWidget(btnShowHistory)
buttonsLayout.addWidget(btnSearchWord)
bottomLayout.addLayout(buttonsLayout)

mainLayout.addLayout(bottomLayout)
mainLayout.addWidget(lblSplittedWordsList)

mainLayout.addWidget(txtTranslations)

strokeCountLayout = QHBoxLayout()
strokeCountLayout.addWidget(lblStrokeCount)
strokeCountLayout.addWidget(spnStrokeCount)
mainLayout.addLayout(strokeCountLayout)
lblStrokeCount.adjustSize()

window.show()
splashScreen.finish(window)
app.exec_()
