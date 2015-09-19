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

names = []
while False:
    print("> ", end="")
    sys.stdout.flush()
    command = sys.stdin.readline().strip()
    if command == "quit": 
        quit()
    elif command == "": 
        continue
    elif command == "clear":
        names = []
        print("cleared")
    elif command[0] == "-":
        pass
    elif command == "debug on":
        print("on")
        debug = True
    elif command == "debug off":
        print("off") 
        debug = False
    # elif command.startswith("get radicals"):
        # kanji = command.split(" ")[2][0]
        
        # print("Radicals for", kanji + ": ", end="")
        # for r, kList in radicalsDb.iter():
            # if kanji in kList:
                # print(r)
        # print("")
    else:
        kanjis = getKanjiFromRadicals(names + [command])
        if len(kanjis) == 0:
            print("No kanji found. Ignoring radical", command)
        else:
            names.append(command)
            
            kanjis = sorted(kanjis, key=kanjidic.getStrokeCount)
            
            for k in kanjis:
                print(k, end="")
            print("")

def ontxtRadicalsInputChanged():
    if debug: print("1")
    kanjis = getKanjiFromRadicals(txtRadicalsInput.text().replace("、", ",").split(","))
    if debug: print("2")
    kanjis = sorted(kanjis, key=kanjidic.getStrokeCount)
    if debug: print("3")
    txt = ""
    for k in kanjis[:100]:
        txt += k
    if len(kanjis) > 100:
        txt += "..."
    if debug: print("4")
    txtOutput.setText(txt)
    if debug: print("5")

def ontxtKanjiInputChanged():
    txt = ""
    for r in radicalsDb.keys():
        if txtKanjiInput.text().strip() in radicalsDb[r]:
            txt += r + " "
    lblRadicals.setText(txt.strip())

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Kanji lookup")
window.resize(500, 600)

mainLayout = QVBoxLayout(window)

txtRadicalsInput = QLineEdit(window)
txtRadicalsInput.textChanged.connect(ontxtRadicalsInputChanged)

txtOutput = QTextEdit(window)
txtOutput.setReadOnly(True)
txtOutput.setStyleSheet("QTextEdit{ font-size: 70px }")

txtKanjiInput = QLineEdit(window)
txtKanjiInput.textChanged.connect(ontxtKanjiInputChanged)

lblRadicals = QLabel(window)

mainLayout.addWidget(txtRadicalsInput)
mainLayout.addWidget(txtOutput)
mainLayout.addWidget(txtKanjiInput)
mainLayout.addWidget(lblRadicals)

window.show()
app.exec_()
