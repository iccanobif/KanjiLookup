import sys
import os
import re
import time
if sys.executable.endswith("pythonw.exe"):
    sys.stderr = open(os.devnull, "w")

from PySide.QtCore import *
from PySide.QtGui import *

import win32con
# import hotkeythread

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
    
        self.edictDictionary = edict.EdictDictionary()
        self.cedictDictionary = cedict.CedictDictionary()
        self.dict = self.edictDictionary
    
        QWidget.__init__(self)
        self.setWindowTitle("Kanji lookup")
        self.resize(500, 600)
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
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
        self.txtOutputAggregation.selectionChanged.connect(self.handleSelectionChangesOrCursorMovements)
        self.txtOutputAggregation.cursorPositionChanged.connect(self.handleSelectionChangesOrCursorMovements)

        self.btnShowRadicals = QPushButton("Show radicals...", self)
        self.btnShowRadicals.clicked.connect(self.onbtnShowRadicalsClicked)

        self.btnShowHistory = QPushButton("History...", self)
        self.btnShowHistory.clicked.connect(self.onbtnShowHistoryClicked)

        self.btnSearchWord = QPushButton("Search...", self)
        self.btnSearchWord.clicked.connect(self.onbtnSearchWordClicked)
        
        self.btnSaveWord = QPushButton("Save word", self)
        self.btnSaveWord.clicked.connect(self.onbtnSaveWordClicked)

        self.lblSplittedWordsList = QLabel(self)
        self.lblSplittedWordsList.setStyleSheet("font-size: 20px")
        self.lblSplittedWordsList.linkActivated.connect(self.onlblSplittedWordsListlinkActivated)

        self.txtTranslations = QTextEdit(self)
        self.txtTranslations.setReadOnly(True)
        self.txtTranslations.setStyleSheet("font-size: 25px")
        #stuff for making HTML a bit faster (http://stackoverflow.com/questions/3120258/qtextedit-inserthtml-is-very-slow)
        self.txtTranslations.setAcceptRichText(False)
        self.txtTranslations.setContextMenuPolicy(Qt.NoContextMenu)
        self.txtTranslations.setUndoRedoEnabled(False)

        self.lblStrokeCount = QLabel("Stroke count:")
        self.spnStrokeCount = QSpinBox(self)
        self.spnStrokeCount.valueChanged.connect(self.onspnStrokeCountValueChanged)
        
        self.rbtChinese = QRadioButton("Chinese", self)
        self.rbtChinese.toggled.connect(self.onLanguageChanged)
        self.rbtJapanese = QRadioButton("Japanese", self)
        self.rbtJapanese.setChecked(True)
        
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
        self.buttonsLayout.addWidget(self.btnSaveWord)
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

        # pid = ctypes.windll.kernel32.GetCurrentProcessId()
        # ctypes.windll.user32.AllowSetForegroundWindow(pid)
        
        # t = hotkeythread.HotkeyThread()
        # t.registerHotkey(win32con.MOD_CONTROL | win32con.MOD_ALT, ord("K"), self.focusWindow, self)
        # t.start()
        
    def focusWindow(self):
        self.showNormal()
        
        self.activateWindow()
        self.raise_()
        self.txtOutputAggregation.setFocus()
        
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
        # print("popup.show()")
        popup.show()
        
    def showTranslations(self, word):
        translations = self.dict.getTranslation(word)
        
        if translations is None:
            self.txtTranslations.setPlainText("-- not found --")
        else:
            # print(str(time.clock()), "self.txtTranslations.setHtml()")
            if len(translations) > 50:
                translations = translations[0:50] + ["..."]
            self.txtTranslations.setHtml("<br/>--------<br/>".join(translations).replace("\n", "<br/>"))
            # print(str(time.clock()), "self.txtTranslations.setHtml() - fine")

    def onbtnShowHistoryClicked(self):
        self.historyWindow.show()
        
    def onspnStrokeCountValueChanged(self, value):
        self.populateList(False)
        
    def onbtnSearchWordClicked(self):
    
        if self.txtOutputAggregation.text().strip() == "":
            return
            
        self.setCursor(Qt.WaitCursor)
            
        text = ""
        if self.txtOutputAggregation.hasSelectedText():
            text = self.txtOutputAggregation.selectedText()
        else:
            text = self.txtOutputAggregation.text()

        popup = ListPopup(self)
        # print("popup.show(self.dict.findWordsFromFragment(text))")
        popup.show(self.dict.findWordsFromFragment(text))
        
        self.unsetCursor()
        
    def onbtnSaveWordClicked(self):
        if self.txtOutputAggregation.hasSelectedText():
            text = self.txtOutputAggregation.selectedText()
        else:
            text = self.txtOutputAggregation.text()
            
        f = open("savedwords.txt", "a", encoding="utf8")
        f.write(text + "\n")
        f.close()
        QMessageBox.information(self, "saved", "saved")
        
    def ontxtOutputAggregationTextChanged(self):
        # print(self.txtOutputAggregation.text())
        self.historyWindow.addEntry(self.txtOutputAggregation.text())
        
        input = self.txtOutputAggregation.text()
        
        if input == "":
            self.txtTranslations.setPlainText("")
            self.lblSplittedWordsList.setText("")
            return
        
        # print(str(time.clock()), "words = self.dict.splitSentence(input)")
        words = self.dict.splitSentence(input)
        
        # print(str(time.clock()), "text = ''")
        text = ""
        for w in words:
            text += "<a href='word'>word</a> ".replace("word", w)
        # print(str(time.clock()), "self.lblSplittedWordsList.setText(text)")
        self.lblSplittedWordsList.setText(text)
                
    def handleSelectionChangesOrCursorMovements(self):
        # print(str(time.clock()), "self.handleSelectionChangesOrCursorMovements() - inizio")
        if self.txtOutputAggregation.hasSelectedText():
            self.showTranslations(self.txtOutputAggregation.selectedText())
        else:
            # This is utter rubbish... Relies on the fact that splitSentence() returns
            # all the extra whitespace between words, and weird things happen when the cursor's
            # between two words
            # merda = len(re.sub("\s*?", "", self.txtOutputAggregation.text()[:newPosition]))
            i = 0
            for w in self.dict.splitSentence(self.txtOutputAggregation.text()):
                if len(w) + i >= self.txtOutputAggregation.cursorPosition():
                    self.showTranslations(w)
                    return
                else:
                    i += len(w)
        
    def onlblSplittedWordsListlinkActivated(self, link):
        self.showTranslations(link)
        
    def onLanguageChanged(self, checked):
        self.setCursor(Qt.WaitCursor)
        if self.rbtChinese.isChecked():
            self.dict = self.cedictDictionary
        else:
            self.dict = self.edictDictionary
        self.ontxtOutputAggregationTextChanged()
        self.unsetCursor()
        
class Popup(QDialog):
    def __init__(self, parent, text):
        print("def __init__(self, parent, text):")
        #va in errore tra qui...
        print("QDialog.__init__(self, parent)")
        QDialog.__init__(self, parent)
        #...e qui
        print("self.setWindowModality(Qt.WindowModal)")
        self.setWindowModality(Qt.WindowModal)
        print("self.setWindowTitle(Kanji lookup)")
        self.setWindowTitle("Kanji lookup")
        print("label = QLabel(self)")
        self.label = QLabel(self) #VA IN ERRORE QUI!!!!!!!
        print("label.setStyleSheet(font-size: 40px)")
        self.label.setStyleSheet("font-size: 40px")
        print("label.setWordWrap(True)")
        self.label.setWordWrap(True)
        print("label.setText(text)")
        self.label.setText(text)
        print("layout = QHBoxLayout(self)")
        self.layout = QHBoxLayout(self)
        print("layout.addWidget(label)")
        self.layout.addWidget(self.label)
        print("self.setLayout(layout)")
        self.setLayout(self.layout)
        print("self.adjustSize()")
        self.adjustSize()
        
class ListPopup(QDialog):
    def __init__(self, parent):
        print("def __init__(self, parent):")
        #va in errore tra qui...
        print("QDialog.__init__(self, parent)")
        QDialog.__init__(self, parent)
        
        print("self.entries = set()")
        self.entries = set()
        
        print("self.list = QListWidget(self)")
        self.list = QListWidget(self)
        print("self.list.setStyleSheet(""font-size: 30px"")")
        self.list.setStyleSheet("font-size: 30px")
        print("layout = QHBoxLayout(self)")
        layout = QHBoxLayout(self)
        print("layout.addWidget(self.list)")
        layout.addWidget(self.list)
        print("self.setLayout(layout)")
        self.setLayout(layout)
        print("FINE def __init__(self, parent):")
        #...e qui
        
    def show(self, items):
        print("def show(self, items):")
        for i in items:
            self.list.addItem(i)
        QDialog.show(self)

window = MainWindow()
window.show()
splashScreen.finish(window)
app.exec_()
# os._exit(0) # Kill the global hotkey thread. This is supposed to be a very bad thing to do, but I'm a very bad person and I do not care.