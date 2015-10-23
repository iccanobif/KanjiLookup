import re
import utf8console

dictionary = None

# EDICT2 entry samples:
# 煆焼;か焼 [かしょう] /(n,vs) calcination/calcining/EntL2819620/
# いらっしゃい(P);いらしゃい(ik) /(int,n) (1) (hon) (used as a polite imperative) (See いらっしゃる・1) come/go/stay/(2) (See いらっしゃいませ) welcome!/(P)/EntL1000920X/

def __loadDictionary():
    global dictionary
    print("Loading edict2...")
    dictionary = dict()
    with open("edict2u", "r", encoding="utf8") as f:
        for line in f.readlines():
            boundary = line.find("/")
            kanjis = line[0:boundary]
            kanjis = re.sub("\[|\]| |\(.*?\)", ";", kanjis) #remove anything that's inside (), 
            for k in kanjis.split(";"):
                if k == "": continue
                if k not in dictionary:
                    dictionary[k] = []
                dictionary[k].append(line)

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