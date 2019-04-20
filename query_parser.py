import re
import nltk
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

stemmer = PorterStemmer()
stopWords = set(stopwords.words('english'))
def queryStringToPhraseAndTermsList(queryString):
    #Retrieves terms and phrases from query string
    termsAndPhraseList = queryString.split('"')
    termsList = []
    for i in range(len(termsAndPhraseList)):
        if i%2:
            # Every odd index is a phrase, we are going to add that in as a term
            phrase = termsAndPhraseList[i]
            phraseTermsList = phraseToTermsList(phrase)
            termsList.append(phraseTermsList)
        elif termsAndPhraseList[i] != "":
            # Every even index consist of terms and "AND" operators
            # We are only interested in the terms here
            termsList.extend([word.lower() for word in termsAndPhraseList[i].split() if word != "AND" ])
    return termsList

def phraseToTermsList(phrase):
    #Converts a phrase to a list of stemmed terms
    termsList = phrase.strip('"').split()
    #filteredList = []
    #for term in termsList:
    #    if term not in stopWords:
    #        filteredList.append(term)
    #for i in range(len(termsList)):
    #    termsList[i] = stemmer.stem(termsList[i].lower())
    return termsList

def filterStopWords(termsList):
    #Converts a phrase to a list of stemmed terms
    filteredList = []
    for term in termsList:
        if term not in stopWords:
            filteredList.append(term)
    return filteredList
