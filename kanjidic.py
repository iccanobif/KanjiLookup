import time

print("Loading kanjidic...", end="", flush=True)
_starttime = time.clock()
_strokeCountDictionary = dict()

for line in open("datasets/kanjidic", "r", encoding="utf8").readlines():
    split = line.split(" ")
    kanji = split[0]
    strokeCount = None
    for field in split:
        if field[0] == "S":
            strokeCount = int(field[1:])
            break
    _strokeCountDictionary[kanji] = strokeCount

def getStrokeCount(kanji):
    if kanji not in _strokeCountDictionary:
        return 999
    return _strokeCountDictionary[kanji]
    
print("OK (" + str(time.clock() - _starttime) + " seconds)")