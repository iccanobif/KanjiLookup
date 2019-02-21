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
        if (event.type() == QEvent.KeyPress):
            if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_R:
                self.txtRadicalsInput.setText("")
                self.txtRadicalsInput.setFocus()
        if object == self:
            if event.type() == QEvent.WindowActivate:
                self.txtOutputAggregation.setFocus()
        if object == self.txtOutputAggregation:
            if (event.type() == QEvent.KeyPress):
                if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Down:
                    self.cmbLanguage.setCurrentIndex((self.cmbLanguage.currentIndex() + 1) % self.cmbLanguage.count() )
                if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Up:
                    self.cmbLanguage.setCurrentIndex((self.cmbLanguage.currentIndex() - 1) % self.cmbLanguage.count() )
                return False
        if object == self.lstKanjiList:
            if (event.type() == QEvent.FocusIn):
                self.lstKanjiList.setMaximumHeight(250)
            if (event.type() == QEvent.FocusOut):
                self.lstKanjiList.setMaximumHeight(30)
        # if I got here, it means it's an event I'll just let Qt handle in its default way
        return QObject.eventFilter(self, object, event)

    def __init__(self):
    
        self.edictDictionary = edict.EdictDictionary(loadEnamdict = True)
        self.cedictDictionary = cedict.CedictDictionary()
        self.kengdicDictionary = kengdic.KengdicDictionary()
        self.dict = self.edictDictionary
        self.splitWords = []
    
        QWidget.__init__(self)
        self.setWindowTitle("Kanji lookup")
        self.resize(320, 1000)
        self.move(1580, 40)
        self.setWindowIcon(QIcon("icon.png"))

        

        self.historyWindow = HistoryWindow(self)

        self.txtRadicalsInput = QLineEdit(self)
        self.txtRadicalsInput.textChanged.connect(self.ontxtRadicalsTextChanged)

        self.lstKanjiList = QListWidget(self)
        self.lstKanjiList.setFlow(QListView.LeftToRight)
        self.lstKanjiList.setWrapping(True)
        self.lstKanjiList.setMaximumHeight(30)
        self.lstKanjiList.itemActivated.connect(self.onlstKanjiListItemActivated)
        self.lstKanjiList.setStyleSheet("QListWidget {font-size: 20px}")
        self.lstKanjiList.installEventFilter(self)

        self.txtOutputAggregation = QTextEdit(self)
        self.txtOutputAggregation.setStyleSheet("font-size: 20px")
        self.txtOutputAggregation.setMaximumHeight(120)
        self.txtOutputAggregation.setTabChangesFocus(True)
        self.txtOutputAggregation.setAcceptRichText(False)
        self.txtOutputAggregation.textChanged.connect(self.ontxtOutputAggregationTextChanged)
        self.txtOutputAggregation.selectionChanged.connect(self.handleSelectionChangesOrCursorMovements)
        self.txtOutputAggregation.cursorPositionChanged.connect(self.handleSelectionChangesOrCursorMovements)
        self.txtOutputAggregation.installEventFilter(self)

        self.installEventFilter(self) # Gotta install this event here because I need txtOutputAggregation to exist

        self.btnSaveWord = QPushButton("Save word", self)
        self.btnSaveWord.clicked.connect(self.onbtnSaveWordClicked)

        self.btnShowRadicals = QPushButton("Radicals...", self)
        self.btnShowRadicals.clicked.connect(self.onbtnShowRadicalsClicked)

        self.btnShowHistory = QPushButton("History...", self)
        self.btnShowHistory.clicked.connect(self.onbtnShowHistoryClicked)

        self.btnSearchWord = QPushButton("Search...", self)
        self.btnSearchWord.clicked.connect(self.onbtnSearchWordClicked)

        self.lblSplitWordsList = QLabel(self)
        self.lblSplitWordsList.setStyleSheet("font-size: 20px")
        self.lblSplitWordsList.linkActivated.connect(self.onlblSplitWordsListlinkActivated)

        self.scrollAreaSplitWordsList = QScrollArea(self)
        self.scrollAreaSplitWordsList.setWidget(self.lblSplitWordsList)
        self.scrollAreaSplitWordsList.setWidgetResizable(True)
        self.scrollAreaSplitWordsList.setMaximumHeight(45)

        self.txtTranslations = QTextBrowser(self)
        self.txtTranslations.setReadOnly(True)
        self.txtTranslations.setOpenLinks(False)
        self.txtTranslations.setStyleSheet("font-size: 20px")
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
        self.chkAlwaysOnTop.setCheckState(Qt.Checked)
        
        self.chkListenToClipboard = QCheckBox("Listen to clipboard", self)
        self.chkListenToClipboard.setCheckState(Qt.Unchecked)
        
        
        #Layout

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addWidget(self.txtRadicalsInput)
        self.mainLayout.addWidget(self.lstKanjiList)

        self.bottomLayout = QHBoxLayout()
        self.bottomLayout.addWidget(self.txtOutputAggregation)
        self.buttonsLayout = QVBoxLayout()
        self.buttonsLayout.addWidget(self.btnSaveWord)
        self.buttonsLayout.addWidget(self.btnShowRadicals)
        self.buttonsLayout.addWidget(self.btnShowHistory)
        self.buttonsLayout.addWidget(self.btnSearchWord)
        self.bottomLayout.addLayout(self.buttonsLayout)

        self.mainLayout.addLayout(self.bottomLayout)
        self.mainLayout.addWidget(self.scrollAreaSplitWordsList)

        self.mainLayout.addWidget(self.txtTranslations)

        self.strokeCountLayout1 = QHBoxLayout()
        self.strokeCountLayout1.addWidget(self.lblStrokeCount)
        self.strokeCountLayout1.addWidget(self.spnStrokeCount)
        self.strokeCountLayout1.addWidget(self.cmbLanguage)
        self.strokeCountLayout2 = QHBoxLayout()
        self.strokeCountLayout2.addWidget(self.chkAlwaysOnTop)
        self.strokeCountLayout2.addWidget(self.chkListenToClipboard)
        self.mainLayout.addLayout(self.strokeCountLayout1)
        self.mainLayout.addLayout(self.strokeCountLayout2)
        self.lblStrokeCount.adjustSize()

        
        QApplication.clipboard().dataChanged.connect(self.clipboardChanged)
        # pid = ctypes.windll.kernel32.GetCurrentProcessId()
        # ctypes.windll.user32.AllowSetForegroundWindow(pid)
        
        # t = hotkeythread.HotkeyThread()
        # t.registerHotkey(win32con.MOD_CONTROL | win32con.MOD_ALT, ord("K"), self.focusWindow, self)
        # t.start()
        
    def clipboardChanged(self):
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
        
        self.lstKanjiList.clear()
        if fullList:
            self.lstKanjiList.addItems(kanjis)
        else:
            self.lstKanjiList.addItems(kanjis[:100])
            if len(kanjis) > 100:
                self.lstKanjiList.addItem("...")
        if len(kanjis) > 0:
            self.lstKanjiList.item(0).setSelected(True)
            if not fullList:
                # it's true when i click the "..." item, i want the scrollbar stay as it is
                self.lstKanjiList.scrollToTop()

    def ontxtRadicalsTextChanged(self):
        self.populateList(False)

    def onlstKanjiListItemActivated(self, item):
        if item.text() == "...":
            self.populateList(True)
            self.lstKanjiList.item(100).setSelected(True)
        else:
            if (QApplication.keyboardModifiers() & Qt.ShiftModifier) == Qt.ShiftModifier:
                self.txtOutputAggregation.setPlainText("")
            self.txtOutputAggregation.insertPlainText(item.text())
            
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

    def updateSplitWordsList(self):
        if self.txtOutputAggregation.toPlainText() == "":
            self.lblSplitWordsList.setText("")
            return
                
        text = ""
        # Relies on the fact that handleSelectionChangesOrCursorMovements() is called
        # before ontxtOutputAggregationTextChanged()
        for w in self.splitWords: 
            text += "<a href='word'>word</a> ".replace("word", w)
        self.lblSplitWordsList.setText(text)
        
    def ontxtOutputAggregationTextChanged(self):
        # print(str(time.clock()), "self.ontxtOutputAggregationTextChanged() - inizio")
        self.historyWindow.addEntry(self.txtOutputAggregation.toPlainText())
        
        self.updateSplitWordsList()

        if self.txtOutputAggregation.toPlainText() == "":
            self.txtTranslations.setPlainText("")
        
    def handleSelectionChangesOrCursorMovements(self):
        # print(str(time.clock()), "self.handleSelectionChangesOrCursorMovements() - inizio")
        if self.txtOutputAggregation.textCursor().hasSelection():
            self.showTranslations(self.txtOutputAggregation.textCursor().selectedText())
        else:
            # This is utter rubbish... Relies on the fact that splitSentence() returns
            # all the extra whitespace between words, and weird things happen when the cursor's
            # between two words
            # merda = len(re.sub("\s*?", "", self.txtOutputAggregation.text()[:newPosition]))
            self.splitWords = self.dict.splitSentence(self.txtOutputAggregation.toPlainText())
            i = 0
            for w in self.splitWords:
                if len(w) + i >= self.txtOutputAggregation.textCursor().position():
                    self.showTranslations(w)
                    return
                else:
                    i += len(w)
        
    def onlblSplitWordsListlinkActivated(self, link):
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
        self.updateSplitWordsList()
        
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
        print("label.setStyleSheet(font-size: 20px)")
        self.label.setStyleSheet("font-size: 20px")
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
        print("self.list.setStyleSheet(""font-size: 20px"")")
        self.list.setStyleSheet("font-size: 20px")
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