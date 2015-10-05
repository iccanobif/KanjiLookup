import re
import utf8console

dictionary = None

# EDICT2 entry sample:
# いらっしゃい(P);いらしゃい(ik) /(int,n) (1) (hon) (used as a polite imperative) (See いらっしゃる・1) come/go/stay/(2) (See いらっしゃいませ) welcome!/(P)/EntL1000920X/

def __loadDictionary():
    global dictionary
    print("Loading edict2...")
    dictionary = dict()
    with open("edict2u", "r", encoding="utf8") as f:
        for line in f.readlines():
            boundary = line.find("/")
            kanjis = line[0:boundary]
            kanjis = re.sub("\[.*?\]", "", kanjis)
            for k in kanjis.split(";"):
                k = re.sub("\(.*?\)", "", k)
                dictionary[k.strip()] = line

__loadDictionary() #comment here to do lazy loading of dictionary

def getTranslation(text):
    if dictionary is None:
        __loadDictionary()
    if text not in dictionary:
        return None
    output = dictionary[text].strip().strip("/")
    output = output[output.find("/")+1:]
    return output[:output.rfind("/")]
    
# print(getTranslation("水"))