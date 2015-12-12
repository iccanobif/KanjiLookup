import re
import utf8console
import time
import dictionary

# CC-CEDICT entry samples:
# 一時半刻 一时半刻 [yi1 shi2 ban4 ke4] /a short time/a little while/
class CedictDictionary(dictionary.Dictionary):

    def __init__(self):
        dictionary.Dictionary.__init__(self)
        self.dictionary = None
        self.__loadDictionary() #comment here to do lazy loading of dictionary

    def __loadDictionary(self):
        print("Loading cc-cedict... ", end="", flush=True)
        starttime = time.clock()
        self.dictionary = dict()
        with open("cedict_ts.u8", "r", encoding="utf8") as f:
            for line in f.readlines():
                i = line.find(" ")
                traditional = line[0:i]
                simplified = line[i+1:line.find(" ", i+1)]
                #reading = line[line.find["["] + 1:line.find["]"]]
                
                
                if traditional not in self.dictionary:
                    self.dictionary[traditional] = []
                self.dictionary[traditional].append(line)
                
                if traditional != simplified:
                    if simplified not in self.dictionary:
                        self.dictionary[simplified] = []
                    self.dictionary[simplified].append(line)
                
                if line[0:2] == "你 ":
                    print(line)
                    print(traditional)
                    print(simplified)
                    print(self.dictionary["你"])
        print("OK (" + str(time.clock() - starttime) + " seconds)")

    def getTranslation(self, text):
        if self.dictionary is None:
            self.__loadDictionary()
        
        if text not in self.dictionary:
            return None
        
        output = []
        for entry in self.dictionary[text]:
            output.append(entry.strip())
        
        return output
        
    def normalizeInput(self, text):
        return text
        
if __name__ == '__main__':
    d = CedictDictionary()
    print(d.getTranslation("安"))
    print(d.getTranslation("你"))
