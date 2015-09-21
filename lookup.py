import utf8console
import sys

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
    
def getRadicalsFromKanji(kanji):
    txt = ""
    for r in radicalsDb.keys():
        if kanji.strip() in radicalsDb[r]:
            txt += r + " "
    return txt.strip()
