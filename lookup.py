#import utf8console
import sys, time

radicalsDb = dict()
cache = dict()
debug = False

print("Loading kradfile...", end="", flush=True)
_starttime = time.clock()
#LOAD KRADFILE
with open("datasets/kradfile-u", "r", encoding="utf8") as f:
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
            if k in radicalsDb.keys(): # k is a kanji under r but is also a radical itself
                for new in radicalsDb[k]:
                    if new not in radicalsDb[r]:
                        keepLooping = True
                        radicalsDb[r].add(new)
    if keepLooping == 0:
        break
print("OK (" + str(time.clock() - _starttime) + " seconds)")

#LOAD KANGXI RADICALS
print("Loading kangxi radicals...", end="", flush=True)
_starttime = time.clock()
wikiRadicals = {}
with open("datasets/radicals", "r", encoding="utf8") as f:
    for line in f.readlines():
        if line[0] == "#": continue
        splitted = line.strip().split("\t")
        wikiRadicals[splitted[0]] = splitted[1].lower()
        
print("OK (" + str(time.clock() - _starttime) + " seconds)")

def getKanjiFromRadicalName(radicalName):
    radicalName = radicalName.strip()
    if radicalName in cache:
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
    
    outputKanjiList = set(radicalsDb[radicalsToFind[0]])
    
    for r in radicalsToFind[1:]:
        for x in radicalsDb[r]:
            outputKanjiList.add(x)
        
    cache[radicalName] = outputKanjiList
    return outputKanjiList

# radicalNames must be a list() of names of radicals
def getKanjiFromRadicals(radicalNames): 
    output = getKanjiFromRadicalName(radicalNames[0])
    
    for r in radicalNames[1:]:
        output = set(filter(lambda x: x in output, getKanjiFromRadicalName(r)))
        
    return output
    
def getRadicalsFromKanji(kanji):
    output = []
    for r in radicalsDb.keys():
        if kanji.strip() in radicalsDb[r]:
            output.append(r)
    return output

def getRadicalName(radical):
    return wikiRadicals[radical]