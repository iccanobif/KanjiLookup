import sys
import os
import re
import time
if sys.executable.endswith("pythonw.exe"):
    sys.stderr = open(os.devnull, "w")

from PySide.QtCore import *
from PySide.QtGui import *
import simpleaudio as sa

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
splashScreen.showMessage("Loading kengdic...")
import kengdic
from historyWindow import HistoryWindow

class MainWindow(QWidget):

    def eventFilter(self, object, event):
        if object == self.txtOutputAggregation:
            if (event.type() == QEvent.KeyPress):
                if event.key() == Qt.Key_Up:
                    self.cmbLanguage.setCurrentIndex((self.cmbLanguage.currentIndex() + 1) % self.cmbLanguage.count() )
                if event.key() == Qt.Key_Down:
                    self.cmbLanguage.setCurrentIndex((self.cmbLanguage.currentIndex() - 1) % self.cmbLanguage.count() )
                return False
        # if I got here, it means it's an event I'll just let Qt handle in its default way
        return QObject.eventFilter(self, object, event)

    def __init__(self):
    
        self.edictDictionary = edict.EdictDictionary(loadToMemory = True, loadEnamdict = True)
        self.cedictDictionary = cedict.CedictDictionary()
        self.kengdicDictionary = kengdic.KengdicDictionary()
        self.dict = self.edictDictionary
    
        QWidget.__init__(self)
        self.setWindowTitle("Kanji lookup")
        self.resize(500, 600)
        self.setWindowIcon(QIcon("icon.png"))

        self.historyWindow = HistoryWindow(self)

        self.txtRadicalsInput = QLineEdit(self)
        self.txtRadicalsInput.textChanged.connect(self.ontxtRadicalsTextChanged)

        self.lstOutput = QListWidget(self)
        self.lstOutput.setFlow(QListView.LeftToRight)
        self.lstOutput.setWrapping(True)
        self.lstOutput.setMaximumHeight(250)
        self.lstOutput.itemActivated.connect(self.onlstOutputItemActivated)
        self.lstOutput.setStyleSheet("QListWidget {font-size: 70px}")

        self.txtOutputAggregation = QTextEdit(self)
        self.txtOutputAggregation.setStyleSheet("font-size: 50px")
        self.txtOutputAggregation.setMaximumHeight(120)
        self.txtOutputAggregation.setTabChangesFocus(True)
        self.txtOutputAggregation.textChanged.connect(self.ontxtOutputAggregationTextChanged)
        self.txtOutputAggregation.selectionChanged.connect(self.handleSelectionChangesOrCursorMovements)
        self.txtOutputAggregation.cursorPositionChanged.connect(self.handleSelectionChangesOrCursorMovements)
        self.txtOutputAggregation.installEventFilter(self)

        self.btnSaveWord = QPushButton("Save word", self)
        self.btnSaveWord.clicked.connect(self.onbtnSaveWordClicked)

        self.btnShowRadicals = QPushButton("Show radicals...", self)
        self.btnShowRadicals.clicked.connect(self.onbtnShowRadicalsClicked)

        self.btnShowHistory = QPushButton("History...", self)
        self.btnShowHistory.clicked.connect(self.onbtnShowHistoryClicked)

        self.btnSearchWord = QPushButton("Search...", self)
        self.btnSearchWord.clicked.connect(self.onbtnSearchWordClicked)
        
        self.lblSplittedWordsList = QLabel(self)
        self.lblSplittedWordsList.setStyleSheet("font-size: 20px")
        self.lblSplittedWordsList.linkActivated.connect(self.onlblSplittedWordsListlinkActivated)

        self.txtTranslations = QTextBrowser(self)
        self.txtTranslations.setReadOnly(True)
        self.txtTranslations.setOpenLinks(False)
        self.txtTranslations.setStyleSheet("font-size: 25px")
        #stuff for making HTML a bit faster (http://stackoverflow.com/questions/3120258/qtextedit-inserthtml-is-very-slow)
        self.txtTranslations.setAcceptRichText(False)
        self.txtTranslations.setContextMenuPolicy(Qt.NoContextMenu)
        self.txtTranslations.setUndoRedoEnabled(False)
        self.txtTranslations.anchorClicked.connect(self.onTxtTranslationsAnchorClicked)

        self.lblStrokeCount = QLabel("Stroke count:")
        self.spnStrokeCount = QSpinBox(self)
        self.spnStrokeCount.valueChanged.connect(self.onspnStrokeCountValueChanged)
        
        self.cmbLanguage = QComboBox(self)
        self.cmbLanguage.addItem("Japanese", "JAPANESE")
        self.cmbLanguage.addItem("Chinese", "CHINESE")
        self.cmbLanguage.addItem("Korean", "KOREAN")
        self.cmbLanguage.currentIndexChanged.connect(self.onLanguageChanged)
                
        self.chkAlwaysOnTop = QCheckBox("AOT", self)
        self.chkAlwaysOnTop.stateChanged.connect(self.onchkAlwaysOnTopStateChanged)
        self.chkAlwaysOnTop.setCheckState(Qt.Unchecked)
        
        self.chkListenToClipboard = QCheckBox("Listen to clipboard", self)
        self.chkListenToClipboard.setCheckState(Qt.Unchecked)
        
        
        #Layout

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addWidget(self.txtRadicalsInput)
        self.mainLayout.addWidget(self.lstOutput)

        self.bottomLayout = QHBoxLayout()
        self.bottomLayout.addWidget(self.txtOutputAggregation)
        self.buttonsLayout = QVBoxLayout()
        self.buttonsLayout.addWidget(self.btnSaveWord)
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
        self.strokeCountLayout.addWidget(self.cmbLanguage)
        self.strokeCountLayout.addWidget(self.chkAlwaysOnTop)
        self.strokeCountLayout.addWidget(self.chkListenToClipboard)
        self.mainLayout.addLayout(self.strokeCountLayout)
        self.lblStrokeCount.adjustSize()

        
        QApplication.clipboard().dataChanged.connect(self.clipboardChanged)
        # pid = ctypes.windll.kernel32.GetCurrentProcessId()
        # ctypes.windll.user32.AllowSetForegroundWindow(pid)
        
        # t = hotkeythread.HotkeyThread()
        # t.registerHotkey(win32con.MOD_CONTROL | win32con.MOD_ALT, ord("K"), self.focusWindow, self)
        # t.start()
        
    def clipboardChanged(self):
        print("clipboardChanged()")
        if self.chkListenToClipboard.checkState() == Qt.Checked:
            self.txtOutputAggregation.setPlainText(QApplication.clipboard().text())
    
        
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
                self.txtOutputAggregation.setPlainText("")
            self.txtOutputAggregation.insert(item.text())
            
    def onbtnShowRadicalsClicked(self):
        text = ""
        for k in self.txtOutputAggregation.toPlainText():
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
    
        if self.txtOutputAggregation.toPlainText().strip() == "":
            return
            
        self.setCursor(Qt.WaitCursor)
            
        text = ""
        if self.txtOutputAggregation.textCursor().hasSelection():
            text = self.txtOutputAggregation.textCursor().selectedText()
        else:
            text = self.txtOutputAggregation.toPlainText()

        popup = ListPopup(self)
        # print("popup.show(self.dict.findWordsFromFragment(text))")
        popup.show(self.dict.findWordsFromFragment(text))
        
        self.unsetCursor()
        
    def onbtnSaveWordClicked(self):
        if self.txtOutputAggregation.textCursor().hasSelection():
            text = self.txtOutputAggregation.textCursor().selectedText()
        else:
            text = self.txtOutputAggregation.toPlainText()
            
        f = open("savedwords.txt", "a", encoding="utf8")
        f.write(text + "\n")
        f.close()
        QMessageBox.information(self, "saved", "saved")
        
    def ontxtOutputAggregationTextChanged(self):
        self.historyWindow.addEntry(self.txtOutputAggregation.toPlainText())
        
        input = self.txtOutputAggregation.toPlainText()
        
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
        if self.txtOutputAggregation.textCursor().hasSelection():
            self.showTranslations(self.txtOutputAggregation.textCursor().selectedText())
        else:
            # This is utter rubbish... Relies on the fact that splitSentence() returns
            # all the extra whitespace between words, and weird things happen when the cursor's
            # between two words
            # merda = len(re.sub("\s*?", "", self.txtOutputAggregation.text()[:newPosition]))
            i = 0
            for w in self.dict.splitSentence(self.txtOutputAggregation.toPlainText()):
                if len(w) + i >= self.txtOutputAggregation.textCursor().position():
                    self.showTranslations(w)
                    return
                else:
                    i += len(w)
        
    def onlblSplittedWordsListlinkActivated(self, link):
        self.showTranslations(link)
        
    def onLanguageChanged(self, checked):
        self.setCursor(Qt.WaitCursor)
        currLanguage = self.cmbLanguage.itemData(self.cmbLanguage.currentIndex())
        if currLanguage == "CHINESE":
            self.dict = self.cedictDictionary
        elif currLanguage == "JAPANESE":
            self.dict = self.edictDictionary
        elif currLanguage == "KOREAN":
            self.dict = self.kengdicDictionary
        self.ontxtOutputAggregationTextChanged()
        self.handleSelectionChangesOrCursorMovements()
        self.unsetCursor()
        
    def onTxtTranslationsAnchorClicked(self, url):
        self.playMp3("datasets/chineseSounds/" + url.path() + ".mp3.wav")
        
    def playMp3(self, path):
        wave_obj = sa.WaveObject.from_wave_file(path)
        play_obj = wave_obj.play()
        # play_obj.wait_done()
    
    def onchkAlwaysOnTopStateChanged(self, state):
        show = self.isVisible()
        #originalPosition = self.mapToGlobal(self.pos())
        if state == Qt.Checked:
            self.setWindowFlags(Qt.WindowStaysOnTopHint)
        else:
            flags = self.windowFlags()
            flags = flags & ~Qt.WindowStaysOnTopHint
            self.setWindowFlags(flags)
        if show:
            self.show()
            #self.move(originalPosition)
        
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