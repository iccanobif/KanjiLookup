import utf8console
import random
import sys
import edict
from PySide.QtCore import *
from PySide.QtGui import *

words = []
currentWord = None
random.seed()
correctWords = 0
wrongWords = 0

edictDictionary = edict.EdictDictionary(loadToMemory = False, loadEnamdict = False)

f = open("savedwords.txt", "r", encoding="utf8")
words = [x.strip() for x in f.readlines()]
f.close()


def loadNewWord():
    global currentWord
    #i = random.randrange(0, 20 if len(words) >= 20 else len(words)) # pesco solo tra le prime N righe
    i = random.randrange(0, len(words))

    if currentWord is words[i]:
        currentWord = words[(i+1) % len(words)]
    else:
        currentWord = words[i]
    lblKanji.setText(currentWord + "<a></a>")

def onReturnPressed():
    global correctWords, wrongWords

    if len(words) == 0: return

    if len(txtInput.text()) > 0 and txtInput.text()[-1] == "ｎ":
        txtInput.setText(txtInput.text()[0:-1] + "ん")

    print("hai scritto", txtInput.text())

    s = ""

    if txtInput.text() == currentWord:
        s += "<font color='green'>CORRECT</font>"
        correctWords += 1
        words.remove(currentWord)
    else:
        s += "<font color='red'>WRONG</font>"
        wrongWords += 1
    s += "<br/><br/>"
    s += "Correct: " + str(correctWords) + " Wrong: " + str(wrongWords)
    s += "<br/><br/>"
    translations = edictDictionary.getTranslation(currentWord)
    if translations is not None:
        s += "<br/>---<br/>".join(translations)
    lblOutput.setText(s)

    if len(words) == 0:
        txtInput.setVisible(False)
    else:
        loadNewWord()
    txtInput.setText("")

#GUI

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Kanji practice")
window.resize(500, 600)

lblKanji = QLabel(window)
f = lblKanji.font()
f.setPointSize(200)
lblKanji.setFont(f)
lblKanji.setAlignment(Qt.AlignHCenter)

txtInput = QLineEdit(window)
txtInput.returnPressed.connect(onReturnPressed)
txtInput.setStyleSheet("QLineEdit{ font-size: 70px }")

lblOutput = QLabel(window)
f = lblOutput.font()
f.setPointSize(20)
lblOutput.setFont(f)
lblOutput.setWordWrap(True)

mainLayout = QVBoxLayout(window)
mainLayout.addWidget(lblKanji)
mainLayout.addWidget(txtInput)
mainLayout.addWidget(lblOutput)

loadNewWord()

window.show()
app.exec_()
