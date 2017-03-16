import re
import utf8console
import time
import romkan
import uuid
import subprocess
import os

# What would be better? Pour all the data from the various text files into separate
# sqlite tables and then merge them together with sql, or put everything in python
# objects, work on those and then make the scripts?
# Maybe with the objects it's better since I'll probably have to change their values
# around a few times before they're ready to be converted into SQL statements.

def escapeSql(text):
    return text.replace("'", "''")

class Article:
    articleId = None
    articleContent = None
    lemmaTextWithPitchAccent = None
    lemmas = []
    conjugatedLemmas = []

    def __init__(self, articleContent):
        self.articleId = uuid.uuid1()
        self.articleContent = articleContent

    def toSqlStatement(self):
        return "insert into ARTICLE (ARTICLE_ID, ARTICLE_CONTENT) values ('{id}', '{content}');\n" \
            .format(id=self.articleId, content=escapeSql(self.articleContent.strip()))


class Lemma:
    lemmaId = None
    lemmaText = None
    uninflectedLemma = None
    articleIds = []

    def __init__(self):
        self.lemmaId = uuid.uuid1()

    def toSqlStatement(self):
        return """insert into LEMMA (LEMMA_ID, LEMMA_TEXT, UNINFLECTED_LEMMA) 
                             values ('{id}', '{text}', '{uninflected}');\n""" \
                .format(id=self.lemmaId,
                        content=escapeSql(lemmaText),
                        uninflected=escapeSql(self.uninflectedLemma))

# class RelLemmaArticle:
#     self.lemmaId = None
#     self.lemmaText = None

#     def toSqlStatement(self):
#         return "insert into REL_LEMMA_ARTICLE (LEMMA_ID, ARTICLE_ID) values ('{lemmaId}', '{articleId}');\n" \
#             .format(lemmaId = self.lemmaId, lemmaText = self.lemmaText)


# GLOBALS
lemmas = dict()  # the key is the lemmaTexts
articles = []
relsLemmaArticle = dict()  # the key is the lemmaId


def getArticlesFromEdict():
    # EDICT2 entry samples:
    # 煆焼;か焼 [かしょう] /(n,vs) calcination/calcining/EntL2819620/
    # いらっしゃい(P);いらしゃい(ik) /(int,n) (1) (hon) (used as a polite imperative)
    # (See いらっしゃる・1) come/go/stay/(2) (See いらっしゃいませ)
    # welcome!/(P)/EntL1000920X/

    # ENAMDICT entry sample:
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

    dictionaryJ2E = None

    def calculateConjugations(words, translation):

        m = re.search(
            "v1|v5aru|v5b|v5g|v5k-s|v5k|v5m|v5n|v5r-i|v5r|v5s|v5t|v5u-s|v5uru|v5u|v5|adj-ix|adj-i", translation)
        if m is None:
            return []
        type = m.group()
        if type in ["v5", "v5aru", "v5r-i", "v5u-s", "v5uru"]:
            return []  # I don't know how to conjugate this stuff (yet)

        newWords = []

        # TODO: imperative

        for w in words:
            if w == "":
                continue

            root = w[:-1]

            def add(w):
                newWords.append(root + w)

            if type == "adj-i":
                add("くない")  # negative
                add("く")    # adverbial form
                add("かった")  # past
                add("くなかった")  # past negative
                add("くて")  # te-form
            if type == "adj-ix":
                newWords.append(w[:-2] + "よくない")  # negative
                newWords.append(w[:-2] + "よく")  # adverbial form
                newWords.append(w[:-2] + "よかった")  # past
                newWords.append(w[:-2] + "よくなかった")  # past negative
                newWords.append(w[:-2] + "よくて")  # te-form
            if type == "v1":
                add("")  # stem
                add("ます")  # masu-form
                add("ない")  # negative
                add("た")  # past
                add("なかった")  # past negative
                add("て")  # -te form
                # potential + passive (they're the same for ichidan verbs...)
                add("られる")
                add("させる")  # causative
                add("よう")  # volitive
                add("たい")  # tai-form
                add("ず")  # zu-form
            elif type == "v5s":
                add("した")  # past
                add("して")  # -te form
            elif type == "v5k":
                add("いた")  # past
                add("いて")  # -te form
            elif type == "v5g":
                add("いだ")  # past
                add("いで")  # -te form
            elif type == "v5k-s":  # for verbs ending in 行く
                add("った")  # past
                add("いて")  # -te form
            elif type in ["v5b", "v5m", "v5n"]:
                add("んだ")  # past
                add("んで")  # -te form
            elif type in ["v5r", "v5t", "v5u"]:
                add("った")  # past
                add("って")  # -te form

            firstNegativeKana = ""
            stemKana = ""
            # potential # volitive
            if type in ["v5k", "v5k-s"]:
                add("ける")
                add("こう")
                stemKana = "き"
                firstNegativeKana = "か"
            if type == "v5g":
                add("げる")
                add("ごう")
                stemKana = "ぎ"
                firstNegativeKana = "が"
            if type == "v5b":
                add("べる")
                add("ぼう")
                stemKana = "び"
                firstNegativeKana = "ば"
            if type == "v5m":
                add("める")
                add("もう")
                stemKana = "み"
                firstNegativeKana = "ま"
            if type == "v5n":
                add("ねる")
                add("のう")
                stemKana = "に"
                firstNegativeKana = "な"
            if type == "v5r":
                add("れる")
                add("ろう")
                stemKana = "り"
                firstNegativeKana = "ら"
            if type == "v5t":
                add("てる")
                add("とう")
                stemKana = "ち"
                firstNegativeKana = "た"
            if type == "v5u":
                add("える")
                add("おう")
                stemKana = "い"
                firstNegativeKana = "わ"
            if type == "v5s":
                add("せる")
                add("そう")
                stemKana = "し"
                firstNegativeKana = "さ"

            if type[0:2] == "v5":
                add(firstNegativeKana + "ない")  # negative
                add(firstNegativeKana + "なかった")  # past negative
                add(firstNegativeKana + "せる")  # causative
                add(firstNegativeKana + "れる")  # passive
                add(firstNegativeKana + "ず")  # zu-form
                add(stemKana)  # stem
                add(stemKana + "たい")  # tai-form
                add(stemKana + "ます")  # masu-form

        return newWords

    dictionaryJ2E = dict()
    
    articles = []

    print("Reading edict")
    with open("datasets/edict2u", "r", encoding="utf8") as f:
        for line in f.readlines():
            # remove entry id (eg. "EntL1000920X")
            entryIdIndex = line.rfind("/Ent")
            if entryIdIndex != -1:
                line = line[:line.rfind("/Ent")]

            boundary = line.find("/")

            kanjis = line[0:boundary].lower()
            # remove anything that's inside ()
            kanjis = re.sub("\[|\]| |\(.*?\)", ";", kanjis)
            kanjis = romkan.katakana_to_hiragana(kanjis)
            kanjis = kanjis.split(";")
            kanjis = list(filter(lambda x: x != "", kanjis))

            conjugations = calculateConjugations(kanjis, line[boundary:])
            
            article = Article(articleContent=line)
            article.lemmas = kanjis
            article.conjugatedLemmas = conjugations
            articles.append(article)
    return articles

    # Use this to clean up kotobank's html
    # entry = entry.replace("</a>", "") \
    #              .replace("</img>", "") \
    #              .replace("</spellout>", "") \
    #              .replace("</section>", "")
    # entry = re.sub("<(a|img|section|spellout) .*?>", "", entry) #remove links

def main():
    articles = getArticlesFromEdict()
    sqlFileName = "builddatabase.sql"
    dbFileName = "db.db"

    with open(sqlFileName, "w", encoding="utf8") as f:
        print("Writing edict")
        f.write("""CREATE TABLE ARTICLE (ARTICLE_ID, ARTICLE_CONTENT); 
                CREATE TABLE LEMMA (LEMMA_TEXT, ARTICLE_ID);
                """)
        f.write("BEGIN TRANSACTION;\n")
        for a in articles:
            f.write(a.toSqlStatement() + "\n")
            for l in a.lemmas + a.conjugatedLemmas:
                f.write("INSERT INTO LEMMA (LEMMA_TEXT, ARTICLE_ID) values ('{text}', '{articleId}');\n" \
                        .format(text=escapeSql(l), articleId=a.articleId))
        f.write("END TRANSACTION;\n")
        f.write("CREATE INDEX IDX_ARTICLE ON ARTICLE(ARTICLE_ID);\n")
        f.write("CREATE INDEX IDX_LEMMA ON LEMMA(LEMMA_TEXT);\n")

    # Da capire come mai non ci sono le coniugazioni di 起こる

    with open(sqlFileName, "r", encoding="utf8") as f:
        if (os.path.isfile(dbFileName)):
            os.remove(dbFileName)
        print("Starting sqlite")
        subprocess.call(["sqlite", dbFileName], stdin=f)
    #os.remove(sqlFileName)
    print("Done")

    # select * from lemma l
    # join article a on a.article_id = l.article_id
    # where l.lemma_text = '起こった'

main()