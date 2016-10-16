import utf8console

# KENGDIC entry sample:
# 140261	전원의  행진	NULL	promenade	1	1	engdic	2006-01-16 00:52:46	19	NULL	140261	t
class KengdicDictionary:

    dictionary = None
    
    def __init__(self):
        self._splitterCache = dict()
        if KengdicDictionary.dictionary is not None:
            self.dictionary = KengdicDictionary.dictionary
        else:
            self.__loadDictionary() #comment here to do lazy loading of dictionary
            
    def __addToDictionary(self, key, content):
        if key not in self.dictionary:
            self.dictionary[key] = set()
        self.dictionary[key].add(content)
        
    def __loadDictionary(self):
        print("Loading KENGDIC... ", end="", flush=True)
        self.dictionary = dict()
        with open("datasets/kengdic_2011.tsv", "r", encoding="utf8") as f:
            for line in f.readlines():
                line = line.strip()
                split = line.split("\t")
                hangul = split[1]
                english = split[3]
                self.__addToDictionary(hangul, hangul + ": " + english)
                for e in english.split(" "):
                    self.__addToDictionary(e, hangul + ": " + english)

    def getTranslation(self, text):
        if self.dictionary is None:
            self.__loadDictionary()
        
        text = text.lower()
        
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
            
        text = text.lower()
        
        output = self.splitSentencePrioritizeFirst(text)
        self._splitterCache[text] = output
        return output
        
if __name__ == '__main__':
    d = KengdicDictionary()
    print("\n\t".join(d.getTranslation("여보세요")))
    
