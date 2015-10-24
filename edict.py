import re
import utf8console
import time

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
    
    #TODO: imperative
    
    for w in words:
        stem = w[:-1] # technically, this is not the stem...
        if type == "v1":
            newWords.append(stem + "ない") # negative
            newWords.append(stem + "た") # past
            newWords.append(stem + "て") # -te form
            # newWords.append(stem + "ている") # -te+iru form
            # newWords.append(stem + "てる") # -te+iru form
            newWords.append(stem + "られる") # potential + passive (they're the same for ichidan verbs...)
            newWords.append(stem + "させる") # causative
            newWords.append(stem + "よう") # volitive
        elif type == "v5s":
            newWords.append(stem + "した") # past
            newWords.append(stem + "して") # -te form
            # newWords.append(stem + "している") # -te+iru form
            # newWords.append(stem + "してる") # -te+iru form
            newWords.append(stem + "せる") # potential
        elif type in ["v5k", "v5g"]:
            newWords.append(stem + "いた") # past
            newWords.append(stem + "いて") # -te form
            # newWords.append(stem + "いている") # -te+iru form
            # newWords.append(stem + "いてる") # -te+iru form
        elif type in ["v5b", "v5m", "v5n"]:
            newWords.append(stem + "んだ") # past
            newWords.append(stem + "んで") # -te form
            # newWords.append(stem + "んでいる") # -te+iru form
            # newWords.append(stem + "んでる") # -te+iru form
        elif type in ["v5r", "v5t", "v5u"]:
            newWords.append(stem + "った") # past
            newWords.append(stem + "って") # -te form
            # newWords.append(stem + "っている") # -te+iru form
            # newWords.append(stem + "ってる") # -te+iru form
        
        firstNegativeKana = ""
        
                          # potential                    # volitive                     
        if type == "v5k": newWords.append(stem + "ける");  newWords.append(stem + "こう"); firstNegativeKana = "か"
        if type == "v5g": newWords.append(stem + "げる");  newWords.append(stem + "ごう"); firstNegativeKana = "が"
        if type == "v5b": newWords.append(stem + "べる");  newWords.append(stem + "ぼう"); firstNegativeKana = "ば"
        if type == "v5m": newWords.append(stem + "める");  newWords.append(stem + "もう"); firstNegativeKana = "ま"
        if type == "v5n": newWords.append(stem + "ねる");  newWords.append(stem + "のう"); firstNegativeKana = "な"
        if type == "v5r": newWords.append(stem + "れる");  newWords.append(stem + "ろう"); firstNegativeKana = "ら"
        if type == "v5t": newWords.append(stem + "てる");  newWords.append(stem + "とう"); firstNegativeKana = "た" 
        if type == "v5u": newWords.append(stem + "える");  newWords.append(stem + "おう"); firstNegativeKana = "わ" 

        newWords.append(stem + firstNegativeKana + "ない") #negative
        newWords.append(stem + firstNegativeKana + "せる")  #causative
        newWords.append(stem + firstNegativeKana + "れる")  #passive

    return newWords
        
def __loadDictionary():
    global dictionary
    print("Loading edict2... ", end="", flush=True)
    starttime = time.clock()
    dictionary = dict()
    with open("edict2u", "r", encoding="utf8") as f:
        for line in f.readlines():
            boundary = line.find("/")
            kanjis = line[0:boundary]
            kanjis = re.sub("\[|\]| |\(.*?\)", ";", kanjis) #remove anything that's inside ()
            kanjis = kanjis.split(";")
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
    if text not in dictionary:
        return None
    
    output = []
    for entry in dictionary[text]:
        entry = entry.strip().strip("/")
        output.append(entry[:entry.rfind("/")])
    
    return output
    
# print(getTranslation("水"))