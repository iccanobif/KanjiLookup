import re
#import utf8console
import time
import romkan
import lookup

# EDICT2 entry samples:
# 煆焼;か焼 [かしょう] /(n,vs) calcination/calcining/EntL2819620/
# いらっしゃい(P);いらしゃい(ik) /(int,n) (1) (hon) (used as a polite imperative) (See いらっしゃる・1) come/go/stay/(2) (See いらっしゃいませ) welcome!/(P)/EntL1000920X/

#ENAMDICT entry sample:
# さより /(f) Sayori/
# さよ子 [さよこ] /(f) Sayoko/

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



class PerformanceStatistics:
    def __init__(self):
        self.lastTime = time.clock()
        self.stats = dict()
        # self.stats["measuring performance"] = []
        
    def done(self, description):
        now = time.clock()
        if description not in self.stats:
            self.stats[description] = []
        self.stats[description].append(now - self.lastTime)
        self.lastTime = now
        # self.stats["measuring performance"].append(time.clock() - now)
        
    def computeAverage(self, description):
        return (self.computeTotal(description) / len(self.stats[description]))
        
    def computeTotal(self, description):
        return sum(self.stats[description])  * 1000
        
    def printStats(self):
        for d in sorted(self.stats.keys(), key=self.computeTotal):
            print(d + ": ")
            print("    average: " + str(self.computeAverage(d)) + " ms")
            print("    total: " + str(self.computeTotal(d)) + " ms")
            print("    max: " + str(max(self.stats[d])*1000) + " ms")
            print("    min: " + str(min(self.stats[d])*1000) + " ms")

class EdictDictionary:

    dictionary = None

    def __init__(self):
        self._splitterCache = dict()
        if EdictDictionary.dictionary is not None:
            self.dictionary = EdictDictionary.dictionary
        else:
            self.__loadDictionary() #comment here to do lazy loading of dictionary
    
    class DictionaryEntry:
        def __init__(self):
            self.translation = ""
            self.isConjugated = False
            self.conjugationType = ""

    def extendWithConjugations(self, words, translation):

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
                add("ず") # zu-form
            elif type == "v5s":
                add("した") # past
                add("して") # -te form
            elif type == "v5k":
                add("いた") # past
                add("いて") # -te form
            elif type == "v5g":
                add("いだ") # past
                add("いで") # -te form
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
                add(firstNegativeKana + "ず")  # zu-form
                add(stemKana) # stem
                add(stemKana + "たい") # tai-form
                add(stemKana + "ます") # masu-form

        return newWords
        
    def __addWordToDictionary(self, word, entry):
        if word not in self.dictionary:
            self.dictionary[word] = [entry]
        else:
            self.dictionary[word].append(entry)
        
    def __loadDictionary(self):
        print("Loading edict2... ", end="", flush=True)
        starttime = time.clock()
        self.dictionary = dict()
        EdictDictionary.dictionary = self.dictionary #make a static copy 
        with open("edict2u", "r", encoding="utf8") as f:
            # stats = PerformanceStatistics()
            for line in f.readlines():
                # stats.done("linea")
                boundary = line.find("/")
                kanjis = line[0:boundary].lower()
                kanjis = re.sub("\[|\]| |\(.*?\)", ";", kanjis) #remove anything that's inside ()
                kanjis = romkan.katakana_to_hiragana(kanjis)
                kanjis = kanjis.split(";")
                kanjis = self.extendWithConjugations(kanjis, line[boundary:])
                
                for k in kanjis:
                    if k == "": continue
                    self.__addWordToDictionary(k, line)
        print("OK (" + str(time.clock() - starttime) + " seconds)")
        print("Loading enamdict... ", end="", flush=True)
        starttime = time.clock()
        with open("enamdict.utf", "r", encoding="utf8") as f:
            for line in f.readlines():
                line = line.strip()
                name = line[0:line.find("/")]
                secondaryReadingStart = name.find("[")
                secondaryReadingEnd = name.find("]")
                if secondaryReadingStart == -1: # there's only one reading
                    self.__addWordToDictionary(name.strip(), line)
                else:
                    self.__addWordToDictionary(name[0:secondaryReadingStart].strip(), line)
                    self.__addWordToDictionary(name[secondaryReadingStart+1:secondaryReadingEnd].strip(), line)
        print("OK (" + str(time.clock() - starttime) + " seconds)")
        # stats.printStats()

    def normalizeInput(self, text):
        text = romkan.to_hiragana(text.replace(" ", ""))    
        text = romkan.katakana_to_hiragana(text.lower())
        return text

    def getTranslation(self, text):
        if self.dictionary is None:
            __loadDictionary()
        
        text = self.normalizeInput(text)
        
        if text not in self.dictionary:
            return None
        
        output = []
        for entry in self.dictionary[text]:
            # print("entry", entry)
            entry = entry.strip().strip("/")
            entryIdIndex = entry.rfind("/Ent") #remove entry id (eg. "EntL1000920X")
            # print("entryIdIndex", entryIdIndex)
            if entryIdIndex != -1:
                output.append(entry[:entry.rfind("/Ent")]) 
            else:
                output.append(entry) 
        
        return output
            
    def findWordsFromFragment(self, text):
        # Replace lists of radical names (ex. "{woman,roof}") with the actual possible kanjis
        for radicalList in re.findall("{.*?}", text):
            splitted = radicalList[1:-1].lower().replace("、", ",").split(",")
            text = text.replace(radicalList, "[" + "|".join(lookup.getKanjiFromRadicals(splitted)) + "]")
        return list(sorted(filter(lambda x: re.search("^" + text + "$", x) is not None, self.dictionary.keys())))
        
    # The following sentence still trips the splitter up: it does がそ/れ instead of が/それ (れ is the stem of ichidan verb れる)...
    # print(splitSentence("あなたがそれを気に入るのはわかっていました。"))
    

    # Always tries to make the first word as long as possible. Not resistant
    # against gibberish
    def splitSentencePrioritizeFirst(self, text):
        if text == "":
            return []
        for i in range(len(text)+1, 0, -1):
            firstWord = text[0:i]
            if self.normalizeInput(firstWord) in self.dictionary:
                return [firstWord] + self.splitSentencePrioritizeFirst(text[i:])
                
        return [text[0]] + self.splitSentencePrioritizeFirst(text[1:])

    # Gibberish resistant
    # Scan the input string for the longest substring that is a real word in the dictionary.
    # Then do the same for what's on the left of said substring and what's on the right.
    # If I can't find any suitable substring, that means that the input is gibberish. Return that as if it were a single word.
    def splitSentencePrioritizeLongest(self, text):
        if len(text) == 1: return [text]
        if text == "": return []
        for length in range(len(text), 0, -1):
            for i in range(0, len(text) - length + 1):
                t = text[i:i+length]
                if self.normalizeInput(t) in self.dictionary:
                    return self.splitSentencePrioritizeLongest(text[0:i]) + [t] + self.splitSentencePrioritizeLongest(text[i+length:])
        return [text]
        
    #TODO: Instead of caching here, avoid calling splitSentence() so often from the UI...

    def splitSentence(self, text):
        if text in self._splitterCache:
            return self._splitterCache[text]
        
        output = self.splitSentencePrioritizeFirst(text)
        self._splitterCache[text] = output
        return output

if __name__ == '__main__':
    d = EdictDictionary()
    # print(d.getTranslation("hiraita"))
    # print(d.getTranslation("泣き"))
    # print(d.getTranslation("食べた"))
    # print(d.getTranslation("泣きたい"))
    # print(d.getTranslation("行った"))
    # print(d.getTranslation("行かない"))
    # print(d.findWordsFromFragment("会{eye,legs}"))
    # print(d.splitSentence("naniwosuru"))
    # print(d.splitSentence("通過した")) # has to split as "通過 した" and not as "通 過した"
    # print(d.splitSentencePrioritizeFirst("通過したhforew opfdsした"))
    # print(d.splitSentencePrioritizeLongest("通過したhforew opfdsした"))
    # print(d.getTranslation("さなえ"))
