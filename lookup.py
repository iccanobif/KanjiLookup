import utf8console
import sys

radicalsDb = dict()
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
        #TODO: currentLineRadicals da sortare
        for r in currentLineRadicals:
            if r not in radicalsDb:
                radicalsDb[r] = set()
            if kanji != r:
                if kanji == "又": print("kanji:", kanji, "r:", r)
                radicalsDb[r].add(kanji)

#Clean empty entries ("radicals" with no associated kanji)
for r in filter(lambda x: len(radicalsDb[x]) == 0, list(radicalsDb.keys())):
    del radicalsDb[r]

#Suck cocks
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

# for r in filter(lambda x: x not in radicalsDb.keys(), wikiRadicals):
    # print(r)
# quit()

def getKanjiFromRadicalName(radicalName):
    if debug: print("Start getKanjiFromRadicalName:", radicalName)
    radicalsToFind = []

    for r in wikiRadicals.keys():
        if radicalName in wikiRadicals[r]:
            radicalsToFind.append(r)
            
    if len(radicalsToFind) == 0:
        return []
        
    print("Using radicals ", end="")
    for r in radicalsToFind:
        print(r, end=" ")
    print("")
    
    outputKanjiList = set(radicalsDb[radicalsToFind[0]])
    
    for r in radicalsToFind[1:]:
        for x in radicalsDb[r]:
            outputKanjiList.add(x)
        
    if debug: print("End getKanjiFromRadicalName:", radicalName)
    return outputKanjiList

    
def getKanjiFromRadicals(radicalNames):
    output = getKanjiFromRadicalName(radicalNames[0])
    
    for r in radicalNames[1:]:
        if debug: print("processing radical name", r)
        output = set(filter(lambda x: x in output, getKanjiFromRadicalName(r)))
        
    return output

names = []
while True:
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
    else:
        kanjis = getKanjiFromRadicals(names + [command])
        if len(kanjis) == 0:
            print("No kanji found. Ignoring radical", command)
        else:
            names.append(command)
            for k in kanjis:
                print(k, end="") #TODO: ordinare per numero di stroke
            print("")

#TODO: Gestire casi come 吸 che è formato da 及, il quale a sua volta è 乃 + 丶, senza che sia citato sotto la voce 吸