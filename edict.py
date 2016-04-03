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

class EdictDictionary:

    connection = None
    
    def __init__(self):
        self._splitterCache = dict()
        self._translationsCache = dict()
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
        if text in self._translationsCache:
            return self._translationsCache[text]

        output = []
        
        text = text.lower()
                 
        text = self.normalizeInput(text)
        
        katakanaText = romkan.hiragana_to_katakana(text)

        query = """
                select ifnull(acc.base_form, '') || ' ' || a.content,
                       1 as o
                  from edict_lemmas l
                  join edict_articles a on a.id = l.articleId
             left join pitch_accents acc on acc.kanji = l.uninflectedLemma
                 where l.lemma = '{0}' 
                 union
                select replace(
                        '<b>' || kl.lemmatitle || ' - ' || kl.lemmasubtitle || ' (' || ifnull(acc.base_form, '') || ')</b><br/>' || ka.content,
                        '()',
                        ''),
                       2 as o
                  from kotobank_lemmas kl
                  join kotobank_rel_lemma_article rel on kl.id = rel.lemmaid
                  join kotobank_articles ka on ka.id = rel.articleId
             left join pitch_accents acc on acc.kanji = kl.lemmatitle
                 where (kl.lemmatitle = '{0}' 
                        or kl.lemmasubtitle = '{1}'
                        or kl.lemmatitle in (select el.uninflectedlemma from edict_lemmas el where el.lemma = '{0}')
                        or kl.lemmasubtitle in (select el.uninflectedlemma from edict_lemmas el where el.lemma = '{0}')
                 ) and ka.dictionary = 'デジタル大辞泉の解説'
                 order by o
                """.format(text.replace("'", "\'"), katakanaText.replace("'", "\'"))

        for entry in self.connection.execute(query).fetchall():
            output.append(entry[0])

        self._translationsCache[text] = output
        
        if output == []:
            return None
        else:
            return output
            
    def existsItem(self, text):
        text = text.lower()
        text = self.normalizeInput(text)
        katakanaText = romkan.hiragana_to_katakana(text)

        query = """
                select 1
                  from edict_lemmas l
                 where lemma = '{0}' 
                 union all
                select 1
                  from kotobank_lemmas kl
                 where lemmatitle = '{0}' 
                 union all
                 select 1
                  from kotobank_lemmas kl
                 where lemmasubtitle = '{1}'
                """.format(text.replace("'", "\'"), katakanaText.replace("'", "\'"))

        return len(self.connection.execute(query).fetchall()) > 0
            
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
