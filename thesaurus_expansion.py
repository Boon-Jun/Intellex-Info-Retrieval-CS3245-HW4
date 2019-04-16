from nltk.corpus import wordnet as wn
from search_utils import *
from boolean_operations import orPosIndex
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.wsd import lesk
from nltk import pos_tag
stemmer = PorterStemmer()
class ThesaurusTermWrapper():
    '''
    A term wrapper that allows us to perform operations on similar terms
    '''
    termDictionary = {}
    def __init__(self, term, context = None):
        self.term = term
        if term in self.__class__.termDictionary:
            self.stemmedTerm = self.__class__.termDictionary[term].stemmedTerm
            self.similarTerms = self.__class__.termDictionary[term].similarTerms
            self.freq = self.__class__.termDictionary[term].freq
            self.postingsList = self.__class__.termDictionary[term].postingsList
        else:
            self.stemmedTerm = stemmer.stem(term)
            #print self.stemmedTerm
            self.similarTerms = None
            self.freq = None
            self.postingsList = None
            self.expandTerm(term, context)
            self.__class__.termDictionary[self.term] = self

    def expandTerm(self, term, context = None):
        if self.similarTerms == None:
            filteredWords = set()
            tagged_terms = []
            POS = None
            if context != None:
                tagged_terms = pos_tag(context)

        #Update part of speech
            for item in tagged_terms:
                if term == item[0]:
                    if item[1][0] == 'J':
                        POS = 'a'
                    elif item[1][0] == 'N':
                        POS = 'n'
                    elif item[1][0] == 'V':
                        POS = 'v'
                    elif item[1][0] == 'R':
                        POS = 'r'
                        break

            '''
            ADD TO SYNSET WITH POS ONLY
            if POS != None:
                synsets = wn.synsets(term, POS)
                for synset in synsets:
                    for lemma in synset.lemmas():
                        filteredWords.add(stemmer.stem(lemma.name()))
            '''
            if context != None:
                #Find similar words with Lesk algorithm
                synset = lesk(context, term, pos = POS)
                if synset is not None:
                    for lemma in synset.lemmas():
                        filteredWords.add(stemmer.stem(lemma.name()))

            self.similarTerms = filteredWords
            self.__class__.termDictionary[self.term] = self

    def generatePostingsList(self, term_dict, postings):
        if self.postingsList == None:
            expandedTermSet = set()
            postingsList = loadPostingList(self.stemmedTerm, term_dict, postings)

            #Prepare first docList
            expandedPostingsList = [[item[0], item[1], item[2]]for item in postingsList]
            #print len(expandedPostingsList)
            for term in self.similarTerms:
                expandedPostingsList = orPosIndex(expandedPostingsList, loadPostingList(term, term_dict, postings))
            #print len(expandedPostingsList)
            for posting in expandedPostingsList:
                posting[2].sort()

            self.postingsList = expandedPostingsList
            self.__class__.termDictionary[self.term] = self
        return self.postingsList

    def generateDocumentFrequency(self, term_dict):
        if self.freq == None:
            docFreq = filterHighIdf(self.stemmedTerm, term_dict)
            count = 1
            for word in self.similarTerms:
                count += 1
                docFreq += filterHighIdf(word, term_dict)
            self.freq = docFreq * 1.0/count if docFreq * 1.0/count > 0 else 1
            self.__class__.termDictionary[self.term] = self
        return self.freq
    @classmethod
    def clearTermStorage(cls):
        #Used for clearing termDictionary after a query
         cls.termDictionary.clear() 