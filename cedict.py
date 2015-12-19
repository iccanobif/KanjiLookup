import re
import utf8console
import time

# CC-CEDICT entry samples:
# 一時半刻 一时半刻 [yi1 shi2 ban4 ke4] /a short time/a little while/
class CedictDictionary:

    dictionary = None
    
    def __init__(self):
        self._splitterCache = dict()
        if CedictDictionary.dictionary is not None:
            self.dictionary = CedictDictionary.dictionary
        else:
            self.__loadDictionary() #comment here to do lazy loading of dictionary

    def __loadDictionary(self):
        print("Loading cc-cedict... ", end="", flush=True)
        starttime = time.clock()
        self.dictionary = dict()
        CedictDictionary.dictionary = self.dictionary #make a static copy 
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
    d = CedictDictionary()
    print(d.getTranslation("安"))
    print(d.getTranslation("你"))
