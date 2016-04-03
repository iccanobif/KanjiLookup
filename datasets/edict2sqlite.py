import re
import utf8console
import time
import romkan
import uuid

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

class EdictDictionary:

    dictionaryJ2E = None
    output = None

    def __init__(self):
        self._splitterCache = dict()
        if EdictDictionary.dictionaryJ2E is not None:
            self.dictionaryJ2E = EdictDictionary.dictionaryJ2E
        else:
            self.__loadDictionary() #comment here to do lazy loading of dictionary
    
    def calculateConjugations(self, words, translation):

        m = re.search("v1|v5aru|v5b|v5g|v5k-s|v5k|v5m|v5n|v5r-i|v5r|v5s|v5t|v5u-s|v5uru|v5u|v5|adj-ix|adj-i", translation)
        if m is None:
            return []
        type = m.group()
        if type in ["v5", "v5aru", "v5r-i", "v5u-s", "v5uru"]:
            return [] # I don't know how to conjugate this stuff (yet)
            
        newWords = []
        
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
        
    def __addWordToDictionaryJ2E(self, word, entry):
        if word not in self.dictionaryJ2E:
            self.dictionaryJ2E[word] = [entry]
        else:
            self.dictionaryJ2E[word].append(entry)
        
    def __loadDictionary(self):
        starttime = time.clock()
        self.dictionaryJ2E = dict()
        EdictDictionary.dictionaryJ2E = self.dictionaryJ2E #make a static copy 
        
        output = open("edict.sql", "w", encoding="utf8")
        output.write("CREATE TABLE IF NOT EXISTS edict_lemmas (lemma, uninflectedLemma, articleId, isInflected);\n")
        output.write("CREATE TABLE IF NOT EXISTS edict_articles (id, content);\n")
        output.write("CREATE INDEX IF NOT EXISTS idx_edict_lemmas_lemma on edict_lemmas (lemma);\n")
        output.write("CREATE INDEX IF NOT EXISTS idx_edict_lemmas_uninfl_lemma on edict_lemmas (uninflectedLemma);\n")
        output.write("CREATE INDEX IF NOT EXISTS idx_edict_articles_id on edict_articles (id);\n")
        output.write("BEGIN TRANSACTION;\n")
        
        with open("edict2u", "r", encoding="utf8") as f:
            # stats = PerformanceStatistics()
            for line in f.readlines():
                entryIdIndex = line.rfind("/Ent") #remove entry id (eg. "EntL1000920X")
                if entryIdIndex != -1:
                    line = line[:line.rfind("/Ent")]
                
                articleid = str(uuid.uuid1())
                output.write("insert into edict_articles (id, content) values ('{id}', '{content}');\n".format(id = articleid, content=line.replace("'", "''")))
                    
                boundary = line.find("/")
                
                kanjis = line[0:boundary].lower()
                kanjis = re.sub("\[|\]| |\(.*?\)", ";", kanjis) #remove anything that's inside ()
                kanjis = romkan.katakana_to_hiragana(kanjis)
                kanjis = kanjis.split(";")
                
                    
                for k in kanjis:
                    if k == "": continue
                    output.write("""insert into edict_lemmas 
                                    (lemma, 
                                    uninflectedLemma, 
                                    articleId, 
                                    isInflected) 
                                values ('{lemma}', 
                                        '{uninflectedLemma}', 
                                        '{articleId}', 
                                        'N');
                            """.format(lemma=k.replace("'", "''"), uninflectedLemma=k.replace("'", "''"), articleId=articleid))
                    
                    conjugations = self.calculateConjugations([k], line[boundary:])
                    
                    for c in conjugations:
                        if c == "": continue
                        output.write("""insert into edict_lemmas 
                                    (lemma, 
                                    uninflectedLemma, 
                                    articleId, 
                                    isInflected) 
                                values ('{lemma}', 
                                        '{uninflectedLemma}', 
                                        '{articleId}', 
                                        'Y');
                                """.format(lemma=c.replace("'", "''"), uninflectedLemma=k.replace("'", "''"), articleId=articleid))
                    
        output.write("END TRANSACTION;\n")

if __name__ == '__main__':
    d = EdictDictionary()
