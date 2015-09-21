from PySide.QtCore import *
from PySide.QtGui import *
import utf8console
import sys
print("Loading kanjidic")
import kanjidic

radicalsDb = dict()
cache = dict()
debug = False

print("Loading kradfile...")
#LOAD KRADFILE
with open("kradfile-u", "r", encoding="utf8") as f:
    for line in f.readlines():
        line = line.strip()
        if line[0] == "#": continue

        splitted = line.strip().split(" ")
        kanji = splitted[0]
        currentLineRadicals = splitted[2:]
        
        for r in currentLineRadicals:
            if r not in radicalsDb:
                radicalsDb[r] = set()
            #if kanji != r:
            radicalsDb[r].add(kanji)

#Clean empty entries ("radicals" with no associated kanji)
for r in filter(lambda x: len(radicalsDb[x]) == 0, list(radicalsDb.keys())):
    del radicalsDb[r]

while True:
    
    keepLooping = False

    for r in radicalsDb.keys():
        for k in list(radicalsDb[r]):
            if k in radicalsDb.keys():
                for new in radicalsDb[k]:
                    if new not in radicalsDb[r]:
                        keepLooping = True
                        radicalsDb[r].add(new)
    if keepLooping == 0:
        break

print("Loading kangxi radicals...")
#LOAD KANGXI RADICALS
wikiRadicals = {}
with open("radicals", "r", encoding="utf8") as f:
    for line in f.readlines():
        if line[0] == "#": continue
        splitted = line.strip().split("\t")
        wikiRadicals[splitted[0]] = splitted[1].lower()

def getKanjiFromRadicalName(radicalName):
    radicalName = radicalName.strip()
    if debug: print("Start getKanjiFromRadicalName:", radicalName)
    if radicalName in cache:
        if debug: print("cache hit:", radicalName)
        return cache[radicalName]
    radicalsToFind = []

    for r in wikiRadicals.keys():
        if radicalName in wikiRadicals[r]:
            radicalsToFind.append(r)
            
    if len(radicalsToFind) == 0:
        if radicalName in radicalsDb: #if radicalName is itself a character, I just look for that
            radicalsToFind = [radicalName] 
        else:
            return []
        
    if debug:
        print("Using radicals ", end="")
        for r in radicalsToFind:
            print(r, end=" ")
        print("")
    
    outputKanjiList = set(radicalsDb[radicalsToFind[0]])
    
    for r in radicalsToFind[1:]:
        for x in radicalsDb[r]:
            outputKanjiList.add(x)
        
    if debug: print("End getKanjiFromRadicalName:", radicalName)
    cache[radicalName] = outputKanjiList
    return outputKanjiList

def getKanjiFromRadicals(radicalNames):
    output = getKanjiFromRadicalName(radicalNames[0])
    
    for r in radicalNames[1:]:
        if debug: print("processing radical name", r)
        output = set(filter(lambda x: x in output, getKanjiFromRadicalName(r)))
        
    return output
    
def kanjiCompare(k):
    strokes = kanjidic.getStrokeCount(k)
    return strokes * 1000000 + ord(k)

def ontxtRadicalsInputChanged():
    kanjis = getKanjiFromRadicals(txtRadicalsInput.text().replace("、", ",").split(","))
    #kanjis = sorted(kanjis, key=kanjidic.getStrokeCount)
    kanjis = sorted(kanjis, key=kanjiCompare)
    lstOutput.clear()
    lstOutput.addItems(kanjis[:100])
    if len(kanjis) > 0:
        lstOutput.itemAt(0, 0).setSelected(True)
        if len(kanjis) > 100:
            lstOutput.addItem("...")

def ontxtKanjiInputChanged():
    txt = ""
    for r in radicalsDb.keys():
        if txtKanjiInput.text().strip() in radicalsDb[r]:
            txt += r + " "
    lblRadicals.setText(txt.strip())
    
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
