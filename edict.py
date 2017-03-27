import re
import utf8console
import time
import romkan
import lookup
import sqlite3

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

def re_fn(expr, item):
    return re.search("^" + expr + "$", item) is not None
    #{tree}造
    #容{mouth}
    try:
        reg = re.compile(expr, re.I)
        return reg.fullmatch(item) is not None
    except:

        print("re_fn(" + expr + ", " + item + ")")
            
class EdictDictionary:

    connection = None
    enamdict = dict()
    
    def __addWordToEnamdict(self, word, entry):
        if word not in self.enamdict:
            self.enamdict[word] = [entry]
        else:
            self.enamdict[word].append(entry)
    
    def __init__(self, loadEnamdict = True):
        self.existsCache = dict()
        self.connection = sqlite3.connect("db.db")
            
        if loadEnamdict == True:
            print("Loading ENAMDICT..")
            with open("datasets/enamdict.utf", "r", encoding="utf8") as f:
                for line in f.readlines():
                    line = line.strip()
                    name = line[0:line.find("/")]
                    secondaryReadingStart = name.find("[")
                    secondaryReadingEnd = name.find("]")
                    if secondaryReadingStart == -1: # there's only one reading
                        self.__addWordToEnamdict(name.strip(), line)
                    else:
                        self.__addWordToEnamdict(name[0:secondaryReadingStart].strip(), line)
                        self.__addWordToEnamdict(name[secondaryReadingStart+1:secondaryReadingEnd].strip(), line)

    def normalizeInput(self, text):
        text = romkan.to_hiragana(text.replace(" ", ""))    
        text = romkan.katakana_to_hiragana(text.lower())
        return text

    def getTranslation(self, text):
        # print(str(time.clock()), "getTranslation(self, text) - INIZIO")

        if text.strip() == "":
            return None
            
        output = []
        
        text = text.lower()
                 
        text = self.normalizeInput(text)
        
        # katakanaText = romkan.hiragana_to_katakana(text) # Why did i do this?

        query = """
                SELECT ARTICLE_CONTENT FROM LEMMA L
                  JOIN ARTICLE A ON A.ARTICLE_ID = L.ARTICLE_ID
                 WHERE L.LEMMA_TEXT = '{text}'
                """.format(text = text.replace("'", "\'"))

        for entry in self.connection.execute(query).fetchall():
            entry = entry[0]
            output.append(entry)

        if text in self.enamdict:
            output += self.enamdict[text]
        
        if output == []:
            return None
        else:
            return output
            

    
    def existsItem(self, text):
        # print(str(time.clock()), "existsItem(self, text) - INIZIO")
        text = text.lower()
        text = self.normalizeInput(text)
        
        if text in self.existsCache:
            return self.existsCache[text]

        if text in self.enamdict:
            return True
        
        katakanaText = romkan.hiragana_to_katakana(text)

        query = """
                SELECT 1
                  FROM LEMMA L
                 WHERE LEMMA_TEXT = '{0}' 
                """.format(text.replace("'", "\'"), katakanaText.replace("'", "\'"))

        output = len(self.connection.execute(query).fetchall()) > 0
        # print(str(time.clock()), "existsItem(self, text) - FINE")
        self.existsCache[text] = output
        return output
            
    def findWordsFromFragment(self, text):
        # Replace lists of radical names (ex. "{woman,roof}") with the actual possible kanjis
        for radicalList in re.findall("{.*?}", text):
            splitted = radicalList[1:-1].lower().replace("、", ",").split(",")
            text = text.replace(radicalList, "[" + "|".join(lookup.getKanjiFromRadicals(splitted)) + "]")
            
        # return list(sorted(filter(lambda x: re.search("^" + text + "$", x) is not None, self.dictionaryJ2E.keys())))
        
        query = """
            SELECT LEMMA
              FROM LEMMA L
             WHERE LEMMA_TEXT REGEXP '{0}' 
            """.format(text.replace("'", "\'"))
            
        return [x[0] for x in self.connection.execute(query).fetchall()]

    # The following sentence still trips the splitter up: it does がそ/れ instead of が/それ (れ is the stem of ichidan verb れる)...
    # print(splitSentence("あなたがそれを気に入るのはわかっていました。"))

    # Always tries to make the first word as long as possible. Not resistant
    # against gibberish
    def splitSentencePrioritizeFirst(self, text):
        if text == "":
            return []
        for i in range(len(text)+1, 0, -1):
            firstWord = text[0:i]
            if self.existsItem(firstWord):
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
                if self.getTranslation(firstWord) is not None:
                    return self.splitSentencePrioritizeLongest(text[0:i]) + [t] + self.splitSentencePrioritizeLongest(text[i+length:])
        return [text]
        
    #TODO: Instead of caching here, avoid calling splitSentence() so often from the UI...

    def splitSentence(self, text):
        # print(str(time.clock()), "splitSentence(self, text) - INIZIO")
        output = self.splitSentencePrioritizeFirst(text)
        # print(str(time.clock()), "splitSentence(self, text) - FINE")
        return output

if __name__ == '__main__':
    d = EdictDictionary(loadToMemory = False, loadEnamdict = False)
    #print(d.getTranslation("hiraita"))
    #print("\n".join(d.dictionaryE2J["me"]))
    # for w in sorted(d.dictionaryE2J.keys(), key=lambda x: -len(d.dictionaryE2J[x])):
        # if len(d.dictionaryE2J[w]) == 1:
            # quit()
        # print(w, len(d.dictionaryE2J[w]))
    # print(d.getTranslation("泣き"))
    # print(d.getTranslation("食べた")) #this has links
    # print(d.getTranslation("彼")) #this has images
    print(str(time.clock()), "about to query 'e'")
    print(len(d.getTranslation("e"))) #this is particularly slow to render
    print(str(time.clock()), "queried 'e'")
    # print(d.getTranslation("泣きたい"))
    # print(d.getTranslation("行った"))
    # print(d.getTranslation("行かない"))
    # print(d.findWordsFromFragment("会{eye,legs}"))
    # print(d.splitSentence("naniwosuru"))
    # print(d.splitSentence("通過した")) # has to split as "通過 した" and not as "通 過した"
    # print(d.splitSentencePrioritizeFirst("通過したhforew opfdsした"))
    # print(d.splitSentencePrioritizeLongest("通過したhforew opfdsした"))
    # print(d.getTranslation("さなえ"))
