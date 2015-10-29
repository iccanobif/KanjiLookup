import re
import utf8console
import time
import romkan

# EDICT2 entry samples:
# 煆焼;か焼 [かしょう] /(n,vs) calcination/calcining/EntL2819620/
# いらっしゃい(P);いらしゃい(ik) /(int,n) (1) (hon) (used as a polite imperative) (See いらっしゃる・1) come/go/stay/(2) (See いらっしゃいませ) welcome!/(P)/EntL1000920X/

# v1 Ichidan verb 
# v5 (godan) verb (not completely classified)  <<--- i'll pretend it's not a verb
# v5aru (godan) verb - -aru special class 
# v5b (godan) verb with `bu' ending 
# v5g (godan) verb with `gu' ending 
# v5k (godan) verb with `ku' ending 
# v5k-s (godan) verb - iku/yuku special class 
# v5m (godan) verb with `mu' ending 
# v5n (godan) verb with `nu' ending 
# v5r (godan) verb with `ru' ending 
# v5r-i (godan) verb with `ru' ending (irregular verb) 
# v5s (godan) verb with `su' ending 
# v5t (godan) verb with `tsu' ending 
# v5u (godan) verb with `u' ending 
# v5u-s (godan) verb with `u' ending (special class) 
# v5uru (godan) verb - uru old class verb (old form of Eru) 

dictionary = None

def extendWithConjugations(words, translation):
    m = re.search("v1|v5aru|v5b|v5g|v5k-s|v5k|v5m|v5n|v5r-i|v5r|v5s|v5t|v5u-s|v5uru|v5u|v5", translation)
    if m is None:
        return words
    type = m.group()
    if type in ["v5", "v5aru", "v5k-s", "v5r-i", "v5u-s", "v5uru"]:
        return words # I don't know how to conjugate this stuff (yet)
    
    newWords = list(words)
    
    def add(w):
        newWords.append(w)
    
    #TODO: imperative
    
    for w in words:
        if w == "":
            continue
        stem = w[:-1] # technically, this is not the stem...
        if type == "v1":
            add(stem) # stem
            add(stem + "ない") # negative
            add(stem + "た") # past
            add(stem + "て") # -te form
            # add(stem + "ている") # -te+iru form
            # add(stem + "てる") # -te+iru form
            add(stem + "られる") # potential + passive (they're the same for ichidan verbs...)
            add(stem + "させる") # causative
            add(stem + "よう") # volitive
        elif type == "v5s":
            add(stem + "した") # past
            add(stem + "して") # -te form
            # add(stem + "している") # -te+iru form
            # add(stem + "してる") # -te+iru form
        elif type in ["v5k", "v5g"]:
            add(stem + "いた") # past
            add(stem + "いて") # -te form
            # add(stem + "いている") # -te+iru form
            # add(stem + "いてる") # -te+iru form
        elif type in ["v5b", "v5m", "v5n"]:
            add(stem + "んだ") # past
            add(stem + "んで") # -te form
            # add(stem + "んでいる") # -te+iru form
            # add(stem + "んでる") # -te+iru form
        elif type in ["v5r", "v5t", "v5u"]:
            add(stem + "った") # past
            add(stem + "って") # -te form
            # add(stem + "っている") # -te+iru form
            # add(stem + "ってる") # -te+iru form
        
        firstNegativeKana = ""
        
        #TODO: Potrei usare romkan per costruire i kana che mi servono a partire dal type (es. se v5g, converto g + o per ottenere ご )
        
                          # potential        # volitive       # real stem                     
        if type == "v5k": add(stem + "ける"); add(stem + "こう"); add(stem + "き"); firstNegativeKana = "か"
        if type == "v5g": add(stem + "げる"); add(stem + "ごう"); add(stem + "ぎ"); firstNegativeKana = "が"
        if type == "v5b": add(stem + "べる"); add(stem + "ぼう"); add(stem + "び"); firstNegativeKana = "ば"
        if type == "v5m": add(stem + "める"); add(stem + "もう"); add(stem + "み"); firstNegativeKana = "ま"
        if type == "v5n": add(stem + "ねる"); add(stem + "のう"); add(stem + "に"); firstNegativeKana = "な"
        if type == "v5r": add(stem + "れる"); add(stem + "ろう"); add(stem + "り"); firstNegativeKana = "ら"
        if type == "v5t": add(stem + "てる"); add(stem + "とう"); add(stem + "ち"); firstNegativeKana = "た" 
        if type == "v5u": add(stem + "える"); add(stem + "おう"); add(stem + "い"); firstNegativeKana = "わ" 
        if type == "v5s": add(stem + "せる"); add(stem + "そう"); add(stem + "し"); firstNegativeKana = "さ" 

        add(stem + firstNegativeKana + "ない") #negative
        add(stem + firstNegativeKana + "せる")  #causative
        add(stem + firstNegativeKana + "れる")  #passive

    return newWords
        
def __loadDictionary():
    global dictionary
    print("Loading edict2... ", end="", flush=True)
    starttime = time.clock()
    dictionary = dict()
    with open("edict2u", "r", encoding="utf8") as f:
        for line in f.readlines():
            boundary = line.find("/")
            kanjis = line[0:boundary].lower()
            kanjis = re.sub("\[|\]| |\(.*?\)", ";", kanjis) #remove anything that's inside ()
            kanjis = kanjis.split(";")
            kanjis = map(romkan.katakana_to_hiragana,kanjis)
            kanjis = extendWithConjugations(kanjis, line[boundary:])
            
            for k in kanjis:
                if k == "": continue
                if k not in dictionary:
                    dictionary[k] = []
                dictionary[k].append(line)
    print("OK (" + str(time.clock() - starttime) + " seconds)")

__loadDictionary() #comment here to do lazy loading of dictionary

def getTranslation(text):
    if dictionary is None:
        __loadDictionary()
        
    text = romkan.katakana_to_hiragana(text.lower())
    if text not in dictionary:
        return None
    
    output = []
    for entry in dictionary[text]:
        entry = entry.strip().strip("/")
        output.append(entry[:entry.rfind("/")])
    
    return output
    
# Always tries to make the first word as long as possible.
# Could it be better to try out every possible split instead, and pick the one with the fewest words?
def splitSentence(text):
    print("splitSentence:", text)
    text = text.strip()
    if text == "":
        return []
    for i in range(len(text)+1, 0, -1):
        firstWord = text[0:i]
        print("    firstWord:", firstWord)
        if firstWord in dictionary:
            return [firstWord] + splitSentence(text[i:])
    return [text]

# This one is still not robust against gibberish...
def splitSentence(text):
    print("splitSentence:", text)
    
    # Corner cases (no need to recurse any further)
    if text == "": return []
    if len(text) == 1:
        if text in dictionary:
            return [text]
        else:
            return None
        return [text]

    # Tries out every possible splitting option
    possibleSolutions = []
    for i in range(1, len(text)+1):
        leftPart = text[0:i]
        if leftPart not in dictionary:
            continue
        rightPart = splitSentence(text[i:])
        if rightPart is None:
            continue
        possibleSolutions.append([leftPart] + rightPart)

    if len(possibleSolutions) == 0:
        return None

    # Find solution with the minimum word count
    minIdx = 0
    for i in range(1, len(possibleSolutions)):
        if len(possibleSolutions[i]) < len(possibleSolutions[minIdx]):
            minIdx = i
    return possibleSolutions[minIdx]

# Maybe this is the right one? Gibberish resistant
# Scan the input string for the longest substring that is a real word in the dictionary.
# Then do the same for what's on the left of said substring and what's on the right.
# If I can't find any suitable substring, that means that the input is gibberish. Return that as if it were a single word.

def splitSentence(text):
    if len(text) == 1: return [text]
    if text == "": return []

    for length in range(len(text), 0, -1):
        # print("length:", length)
        for i in range(0, len(text) - length + 1):
            # print("i:", i)
            t = text[i:i+length]
            # print("    " + t)
            if t in dictionary:
                return splitSentence(text[0:i]) + [t] + splitSentence(text[i+length:])
    return [text]
    
# The following sentence still trips the splitter up: it does がそ/れ instead of が/それ (れ is the stem of ichidan verb れる)...
# print(splitSentence("あなたがそれを気に入るのはわかっていました。"))
# I could try to make words weighted (to make uninflected words like がそ preferable to れ), but it still wouldn't be enough
# print(splitSentence("女の子がとてもぱぷぺｐｄｐｆｄｓぱんｄねＴＰＯあねせるｄねおｄぉうううえかわいいですけど"))
# print(splitSentence("ぱぷぺｐｄｐｆｄｓぱんｄねＴＰＯあねせるｄねおｄぉうううえ"))
# print(splitSentence("読むことが出来ないよね"))
# print(getTranslation("ＴＰＯ"))
# print(getTranslation(romkan.to_hiragana("ＴＰＯ".replace(" ", ""))))
# print(romkan.katakana_to_hiragana("ＴＰＯ") == "ＴＰＯ")
# print(getTranslation("むずむず"))
