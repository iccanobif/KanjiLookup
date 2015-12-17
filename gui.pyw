import sys
import os
import re
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
splashScreen.showMessage("Loading cedict...")
import cedict
splashScreen.showMessage("Loading edict...")
import edict
from historyWindow import HistoryWindow

class MainWindow(QWidget):

    def __init__(self):
    
        self.dict = cedict.CedictDictionary()
    
        QWidget.__init__(self)
        self.setWindowTitle("Kanji lookup")
        self.resize(500, 600)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon("icon.png"))

        self.historyWindow = HistoryWindow(self)

        self.txtRadicalsInput = QLineEdit(self)
        self.txtRadicalsInput.textChanged.connect(self.ontxtRadicalsTextChanged)

        self.lstOutput = QListWidget(self)
        self.lstOutput.setFlow(QListView.LeftToRight)
        self.lstOutput.setWrapping(True)
        self.lstOutput.itemActivated.connect(self.onlstOutputItemActivated)
        self.lstOutput.setStyleSheet("QListWidget {font-size: 70px}")

        self.txtOutputAggregation = QLineEdit(self)
        self.txtOutputAggregation.setStyleSheet("font-size: 70px")
        self.txtOutputAggregation.textChanged.connect(self.ontxtOutputAggregationTextChanged)
        self.txtOutputAggregation.selectionChanged.connect(self.ontxtOutputAggregationSelectionChanged)
        self.txtOutputAggregation.cursorPositionChanged.connect(self.ontxtOutputAggregationCursorPositionChanged)

        self.btnShowRadicals = QPushButton("Show radicals...", self)
        self.btnShowRadicals.clicked.connect(self.onbtnShowRadicalsClicked)

        self.btnShowHistory = QPushButton("History...", self)
        self.btnShowHistory.clicked.connect(self.onbtnShowHistoryClicked)

        self.btnSearchWord = QPushButton("Search...", self)
        self.btnSearchWord.clicked.connect(self.onbtnSearchWordClicked)

        self.lblSplittedWordsList = QLabel(self)
        self.lblSplittedWordsList.setStyleSheet("font-size: 20px")
        self.lblSplittedWordsList.linkActivated.connect(self.onlblSplittedWordsListlinkActivated)

        self.txtTranslations = QTextEdit(self)
        self.txtTranslations.setReadOnly(True)
        self.txtTranslations.setStyleSheet("font-size: 25px")

        self.lblStrokeCount = QLabel("Stroke count:")
        self.spnStrokeCount = QSpinBox(self)
        self.spnStrokeCount.valueChanged.connect(self.onspnStrokeCountValueChanged)
        
        self.rbtChinese = QRadioButton("Chinese", self)
        self.rbtChinese.setChecked(True)
        self.rbtChinese.toggled.connect(self.onLanguageChanged)
        self.rbtJapanese = QRadioButton("Japanese", self)
        
        #Layout

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addWidget(self.txtRadicalsInput)
        self.mainLayout.addWidget(self.lstOutput)

        self.bottomLayout = QHBoxLayout()
        self.bottomLayout.addWidget(self.txtOutputAggregation)
        self.buttonsLayout = QVBoxLayout()
        self.buttonsLayout.addWidget(self.btnShowRadicals)
        self.buttonsLayout.addWidget(self.btnShowHistory)
        self.buttonsLayout.addWidget(self.btnSearchWord)
        self.bottomLayout.addLayout(self.buttonsLayout)

        self.mainLayout.addLayout(self.bottomLayout)
        self.mainLayout.addWidget(self.lblSplittedWordsList)

        self.mainLayout.addWidget(self.txtTranslations)

        self.strokeCountLayout = QHBoxLayout()
        self.strokeCountLayout.addWidget(self.lblStrokeCount)
        self.strokeCountLayout.addWidget(self.spnStrokeCount)
        self.strokeCountLayout.addWidget(self.rbtChinese)
        self.strokeCountLayout.addWidget(self.rbtJapanese)
        self.mainLayout.addLayout(self.strokeCountLayout)
        self.lblStrokeCount.adjustSize()
        
    def resizeEvent(self, event):
        self.populateList(False)
        
    def populateList(self, fullList):
        kanjis = lookup.getKanjiFromRadicals(self.txtRadicalsInput.text().lower().replace("、", ",").split(","))
        # Sorting first by ord() value and then by stroke count, I ensure that kanji
        # with the same stoke count will always be ordered in a consistent way (by ord() value)
        kanjis = sorted(kanjis, key=ord)
        kanjis = sorted(kanjis, key=kanjidic.getStrokeCount)
        
        if self.spnStrokeCount.value() > 0:
            kanjis = list(filter(lambda x: kanjidic.getStrokeCount(x) == self.spnStrokeCount.value(), kanjis))
        
        self.lstOutput.clear()
        if fullList:
            self.lstOutput.addItems(kanjis)
        else:
            self.lstOutput.addItems(kanjis[:100])
            if len(kanjis) > 100:
                self.lstOutput.addItem("...")
        if len(kanjis) > 0:
            self.lstOutput.item(0).setSelected(True)
            if not fullList:
                # it's true when i click the "..." item, i want the scrollbar stay as it is
                self.lstOutput.scrollToTop()

    def ontxtRadicalsTextChanged(self):
        self.populateList(False)

    def onlstOutputItemActivated(self, item):
        if item.text() == "...":
            self.populateList(True)
            self.lstOutput.item(100).setSelected(True)
        else:
            if (QApplication.keyboardModifiers() & Qt.ShiftModifier) == Qt.ShiftModifier:
                self.txtOutputAggregation.setText("")
            self.txtOutputAggregation.insert(item.text())
            
    def onbtnShowRadicalsClicked(self):
        text = ""
        for k in self.txtOutputAggregation.text():
            radicals = lookup.getRadicalsFromKanji(k)
            if len(radicals) == 0: continue
            
            if text != "": text += "<br/>"
            text += k + ":<br/>"
            
            for r in radicals:
                text += r + ": " + lookup.getRadicalName(r) + "<br/>"

        popup = Popup(self, text)
        popup.show()
        
    def showTranslations(self, word):
        translations = self.dict.getTranslation(word)
        
        if translations is None:
            self.txtTranslations.setPlainText("-- not found --")
        else:
            self.txtTranslations.setPlainText("\n--------\n".join(translations))

    def onbtnShowHistoryClicked(self):
        self.historyWindow.show()
        
    def onspnStrokeCountValueChanged(self, value):
        self.populateList(False)
        
    def onbtnSearchWordClicked(self):
        if self.txtOutputAggregation.text().strip() == "":
            return
            
        text = ""
        if self.txtOutputAggregation.hasSelectedText():
            text = self.txtOutputAggregation.selectedText()
        else:
            text = self.txtOutputAggregation.text()

        popup = ListPopup(self)
        popup.show(self.dict.findWordsFromFragment(text))
        
        
    def ontxtOutputAggregationTextChanged(self):
        self.historyWindow.addEntry(self.txtOutputAggregation.text())
        
        input = self.txtOutputAggregation.text()
        
        if input == "":
            self.txtTranslations.setPlainText("")
            self.lblSplittedWordsList.setText("")
            return
        
        words = self.dict.splitSentence(input)
        
        self.showTranslations(words[0])
        
        text = ""
        for w in words:
            text += "<a href='word'>word</a> ".replace("word", w)
        self.lblSplittedWordsList.setText(text)
        
    def ontxtOutputAggregationSelectionChanged(self):
        if self.txtOutputAggregation.hasSelectedText():
            self.showTranslations(self.txtOutputAggregation.selectedText())
        else:
            self.showTranslations(self.txtOutputAggregation.text())

    def ontxtOutputAggregationCursorPositionChanged(self, oldPosition, newPosition):
        if self.txtOutputAggregation.hasSelectedText(): 
            return # Let ontxtOutputAggregationSelectionChanged() handle this
        
        # This is utter rubbish... Relies on the fact that splitSentence() returns
        # all the extra whitespace between words, and weird things happen when the cursor's
        # between two words
        # merda = len(re.sub("\s*?", "", self.txtOutputAggregation.text()[:newPosition]))
        i = 0
        for w in self.dict.splitSentence(self.txtOutputAggregation.text()):
            if len(w) + i > newPosition:
                self.showTranslations(w)
                return
            else:
                i += len(w)
        
    def onlblSplittedWordsListlinkActivated(self, link):
        self.showTranslations(link)
        
    def onLanguageChanged(self, checked):
        if self.rbtChinese.isChecked():
            self.dict = cedict.CedictDictionary()
        else:
            self.dict = edict.EdictDictionary()
        
class Popup(QDialog):
    def __init__(self, parent, text):
        QDialog.__init__(self, parent)
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle("Kanji lookup")
        
        label = QLabel(self)
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
window.show()
splashScreen.finish(window)
app.exec_()
