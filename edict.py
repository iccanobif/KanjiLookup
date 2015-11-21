import re
import utf8console
import time
import romkan
import lookup

# EDICT2 entry samples:
# 煆焼;か焼 [かしょう] /(n,vs) calcination/calcining/EntL2819620/
# いらっしゃい(P);いらしゃい(ik) /(int,n) (1) (hon) (used as a polite imperative) (See いらっしゃる・1) come/go/stay/(2) (See いらっしゃいませ) welcome!/(P)/EntL1000920X/

# v1 Ichidan verb <<-- OK
# v5 (godan) verb (not completely classified)  <<--- i'll pretend it's not a verb
# v5aru (godan) verb - -aru special class (stuff like 下さる and いらっしゃる)  <<--- no need to conjugate these, i guess
# v5b (godan) verb with `bu' ending <<-- OK
# v5g (godan) verb with `gu' ending <<-- OK
# v5k (godan) verb with `ku' ending <<-- OK
# v5k-s (godan) verb - iku/yuku special class <<-- OK
# v5m (godan) verb with `mu' ending <<-- OK
# v5n (godan) verb with `nu' ending <<-- OK
# v5r (godan) verb with `ru' ending <<-- OK
# v5r-i (godan) verb with `ru' ending (irregular verb)  <-- basically, stuff that ends in ある
# v5s (godan) verb with `su' ending <<-- OK
# v5t (godan) verb with `tsu' ending <<-- OK
# v5u (godan) verb with `u' ending <<-- OK
# v5u-s (godan) verb with `u' ending (special class) 
# v5uru (godan) verb - uru old class verb (old form of Eru) 

dictionary = None

class DictionaryEntry:
    def __init__(self):
        self.translation = ""
        self.isConjugated = False
        self.conjugationType = ""

def extendWithConjugations(words, translation):

    m = re.search("v1|v5aru|v5b|v5g|v5k-s|v5k|v5m|v5n|v5r-i|v5r|v5s|v5t|v5u-s|v5uru|v5u|v5|adj-ix|adj-i", translation)
    if m is None:
        return words
    type = m.group()
    if type in ["v5", "v5aru", "v5r-i", "v5u-s", "v5uru"]:
        return words # I don't know how to conjugate this stuff (yet)
        
    newWords = list(words)
    
    
    #TODO: imperative
    
    for w in words:
        if w == "":
            continue
        
        root = w[:-1]
        def add(w):
            newWords.append(root + w)
            
        if type == "adj-i":
            add("くない") # negative
            add("く")    # adverbial form
            add("かった") # past
            add("くなかった") # past negative
            add("くて") # te-form
        if type == "adj-ix":
            newWords.append(w[:-2] + "よくない") # negative
            newWords.append(w[:-2] + "よく") # adverbial form
            newWords.append(w[:-2] + "よかった") # past
            newWords.append(w[:-2] + "よくなかった") # past negative
            newWords.append(w[:-2] + "よくて") # te-form
        if type == "v1":
            add("") # stem
            add("ます") # masu-form
            add("ない") # negative
            add("た") # past
            add("なかった") # past negative
            add("て") # -te form
            add("られる") # potential + passive (they're the same for ichidan verbs...)
            add("させる") # causative
            add("よう") # volitive
            add("たい") # tai-form
        elif type == "v5s":
            add("した") # past
            add("して") # -te form
        elif type in ["v5k", "v5g"]:
            add("いた") # past
            add("いて") # -te form
        elif type == "v5k-s": # for verbs ending in 行く
            add("った") # past
            add("いて") # -te form
        elif type in ["v5b", "v5m", "v5n"]:
            add("んだ") # past
            add("んで") # -te form
        elif type in ["v5r", "v5t", "v5u"]:
            add("った") # past
            add("って") # -te form
        
        firstNegativeKana = ""
        stemKana = ""
        
                                     # potential # volitive   
        if type in ["v5k", "v5k-s"]: add("ける"); add("こう"); stemKana = "き"; firstNegativeKana = "か"
        if type == "v5g":            add("げる"); add("ごう"); stemKana = "ぎ"; firstNegativeKana = "が"
        if type == "v5b":            add("べる"); add("ぼう"); stemKana = "び"; firstNegativeKana = "ば"
        if type == "v5m":            add("める"); add("もう"); stemKana = "み"; firstNegativeKana = "ま"
        if type == "v5n":            add("ねる"); add("のう"); stemKana = "に"; firstNegativeKana = "な"
        if type == "v5r":            add("れる"); add("ろう"); stemKana = "り"; firstNegativeKana = "ら"
        if type == "v5t":            add("てる"); add("とう"); stemKana = "ち"; firstNegativeKana = "た" 
        if type == "v5u":            add("える"); add("おう"); stemKana = "い"; firstNegativeKana = "わ" 
        if type == "v5s":            add("せる"); add("そう"); stemKana = "し"; firstNegativeKana = "さ" 

        if type[0:2] == "v5":
            add(firstNegativeKana + "ない")  # negative
            add(firstNegativeKana + "なかった")  # past negative
            add(firstNegativeKana + "せる")  # causative
            add(firstNegativeKana + "れる")  # passive
            add(stemKana) # stem
            add(stemKana + "たい") # tai-form
            add(stemKana + "ます") # masu-form

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
            kanjis = list(map(romkan.katakana_to_hiragana,kanjis))
            kanjis = extendWithConjugations(kanjis, line[boundary:])
            
            for k in kanjis:
                if k == "": continue
                if k not in dictionary:
                    dictionary[k] = []
                dictionary[k].append(line)
    print("OK (" + str(time.clock() - starttime) + " seconds)")

__loadDictionary() #comment here to do lazy loading of dictionary

def normalizeInput(text):
    text = romkan.to_hiragana(text.replace(" ", ""))    
    text = romkan.katakana_to_hiragana(text.lower())
    return text

def getTranslation(text):
    if dictionary is None:
        __loadDictionary()
    
    text = normalizeInput(text)
    
    if text not in dictionary:
        return None
    
    output = []
    for entry in dictionary[text]:
        entry = entry.strip().strip("/")
        output.append(entry[:entry.rfind("/")])
    
    return output
    
# Always tries to make the first word as long as possible. Not resistant
# against gibberish
def splitSentencePrioritizeFirst(text):
    if text == "":
        return []
    for i in range(len(text)+1, 0, -1):
        firstWord = text[0:i]
        if normalizeInput(firstWord) in dictionary:
            return [firstWord] + splitSentencePrioritizeFirst(text[i:])
            
    return [text[0]] + splitSentencePrioritizeFirst(text[1:])


# Gibberish resistant
# Scan the input string for the longest substring that is a real word in the dictionary.
# Then do the same for what's on the left of said substring and what's on the right.
# If I can't find any suitable substring, that means that the input is gibberish. Return that as if it were a single word.
def splitSentencePrioritizeLongest(text):
    if len(text) == 1: return [text]
    if text == "": return []
    for length in range(len(text), 0, -1):
        for i in range(0, len(text) - length + 1):
            t = text[i:i+length]
            if normalizeInput(t) in dictionary:
                return splitSentencePrioritizeLongest(text[0:i]) + [t] + splitSentencePrioritizeLongest(text[i+length:])
    return [text]
    
#TODO: Instead of caching here, avoid calling splitSentence() so often from the UI...
_splitterCache = dict()
def splitSentence(text):
    if text in _splitterCache:
        return _splitterCache[text]
    
    output = splitSentencePrioritizeFirst(text)
    _splitterCache[text] = output
    return output
        
def findWordsFromFragment(text):
    # Replace lists of radical names (ex. "{woman,roof}") with the actual possible kanjis
    for radicalList in re.findall("{.*?}", text):
        splitted = radicalList[1:-1].lower().replace("、", ",").split(",")
        text = text.replace(radicalList, "[" + "|".join(lookup.getKanjiFromRadicals(splitted)) + "]")
    return list(sorted(filter(lambda x: re.search("^" + text + "$", x) is not None, dictionary.keys())))
    
# The following sentence still trips the splitter up: it does がそ/れ instead of が/それ (れ is the stem of ichidan verb れる)...
# print(splitSentence("あなたがそれを気に入るのはわかっていました。"))

if __name__ == '__main__':
    print(getTranslation("hiraita"))
    print(getTranslation("泣き"))
    print(getTranslation("食べた"))
    print(getTranslation("泣きたい"))
    print(getTranslation("行った"))
    print(getTranslation("行かない"))
    print(findWordsFromFragment("会{eye,legs}"))
    print(splitSentence("naniwosuru"))
    print(splitSentence("通過した")) # has to split as "通過 した" and not as "通 過した"
    print(splitSentencePrioritizeFirst("通過したhforew opfdsした"))
    print(splitSentencePrioritizeLongest("通過したhforew opfdsした"))