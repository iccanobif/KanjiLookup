import re
import utf8console
import time
import romkan
import lookup
import sqlite3

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

    connection = None
    
    def __init__(self):
        self._splitterCache = dict()
        self.connection = sqlite3.connect("db.db")
    
    class DictionaryEntry:
        def __init__(self):
            self.translation = ""
            self.isConjugated = False
            self.conjugationType = ""
        
    def normalizeInput(self, text):
        text = romkan.to_hiragana(text.replace(" ", ""))    
        text = romkan.katakana_to_hiragana(text.lower())
        return text

    def getTranslation(self, text):
            
        output = []
        
        text = text.lower()
                 
        text = self.normalizeInput(text)
        
        query = """
                select a.content
                  from edict_lemmas l
                  join edict_articles a on a.id = l.articleId
                 where lemma = '{}' 
                 """.format(text.replace("'", "\'"))
        
        for entry in self.connection.execute(query).fetchall():
            output.append(entry[0])
        
        katakanaText = romkan.hiragana_to_katakana(text)

        query = """
                select '<b>' || kl.lemmatitle || ' - ' || kl.lemmasubtitle || '</b><br/>' || ka.content
                  from kotobank_lemmas kl
                  join kotobank_rel_lemma_article rel on kl.id = rel.lemmaid
                  join kotobank_articles ka on ka.id = rel.articleId
                 where lemmatitle = '{}' 
                       and ka.dictionary = 'デジタル大辞泉の解説'
                 union
                 select '<b>' || kl.lemmatitle || ' - ' || kl.lemmasubtitle || '</b><br/>' || ka.content
                  from kotobank_lemmas kl
                  join kotobank_rel_lemma_article rel on kl.id = rel.lemmaid
                  join kotobank_articles ka on ka.id = rel.articleId
                 where lemmasubtitle = '{}' 
                       and ka.dictionary = 'デジタル大辞泉の解説'
                """.format(text.replace("'", "\'"), katakanaText.replace("'", "\'"))
                
        for entry in self.connection.execute(query).fetchall():
            output.append(entry[0])

        if output == []:
            return None
        else:
            return output
            
    def findWordsFromFragment(self, text):
        # Replace lists of radical names (ex. "{woman,roof}") with the actual possible kanjis
        for radicalList in re.findall("{.*?}", text):
            splitted = radicalList[1:-1].lower().replace("、", ",").split(",")
            text = text.replace(radicalList, "[" + "|".join(lookup.getKanjiFromRadicals(splitted)) + "]")
        return list(sorted(filter(lambda x: re.search("^" + text + "$", x) is not None, self.dictionaryJ2E.keys())))
        
    # The following sentence still trips the splitter up: it does がそ/れ instead of が/それ (れ is the stem of ichidan verb れる)...
    # print(splitSentence("あなたがそれを気に入るのはわかっていました。"))
    

    # Always tries to make the first word as long as possible. Not resistant
    # against gibberish
    def splitSentencePrioritizeFirst(self, text):
        if text == "":
            return []
        for i in range(len(text)+1, 0, -1):
            firstWord = text[0:i]
            # if self.normalizeInput(firstWord) in self.dictionaryJ2E:
            if self.getTranslation(firstWord) is not None:
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
        if text in self._splitterCache:
            return self._splitterCache[text]
        
        output = self.splitSentencePrioritizeFirst(text)
        self._splitterCache[text] = output
        return output

if __name__ == '__main__':
    d = EdictDictionary()
    #print(d.getTranslation("hiraita"))
    #print("\n".join(d.dictionaryE2J["me"]))
    # for w in sorted(d.dictionaryE2J.keys(), key=lambda x: -len(d.dictionaryE2J[x])):
        # if len(d.dictionaryE2J[w]) == 1:
            # quit()
        # print(w, len(d.dictionaryE2J[w]))
    print(d.getTranslation("泣き"))
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
