import os
import sys
import re
import nltk.tag
import string
from os import listdir
from os.path import isfile, join
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer

class nonDocBasedDataSet:
    
    def __init__(self, pathList):
        self.engStopWords = set(stopwords.words('english'))
        self.excludeSet = set(string.punctuation)
        self.excludeSet = self.excludeSet.union(self.engStopWords)
        extra = set(['also', 'e.g.', 'etc', 'et al.', 'et'])
        self.excludeSet = self.excludeSet.union(extra)
        self.lmtzr = WordNetLemmatizer()
        self.stemmer = SnowballStemmer("english")

        
        onlyfiles = [f for f in listdir(pathList[0]) if isfile(join(pathList[0], f))]
        docI = 0
        docA = 0
        docKE = 0
        for f in onlyfiles:
            if f.startswith('.'):
                continue
            print('Reading from: ', f)
            x = pathList[2]+ '/' + f
            fopen = open(x, 'r', errors='ignore')
            lines = fopen.readlines() #read the body
            bwords = self.splitWords(lines)
            fopen.close()
            print('Words in original file: ', bwords)
            print('#total:: ', len(bwords))
            
            absF = pathList[0] + '/'+f
            fopen = open(absF, 'r', errors='ignore')
            abslines = fopen.read() #read the abstracts
            absSentences = nltk.sent_tokenize(abslines)
            awords = self.splitWords(absSentences)
            fopen.close()
            if len(awords) > 0:
                 docI += 1
            print('Words in abstract: ', awords)
            print('#total:: ', len(awords))
            
            z = awords.difference(bwords)
            print(z)
            
            if len(z) > 0:
                docA += 1
               
            keF = pathList[1] + '/'+f
            fopen = open(keF, 'r', errors='ignore')
            kelines = fopen.read() #read the keyphrases
            fopen.close()
            kewords = set(self.splitKeywords(kelines))
            kz = kewords.difference(bwords)
            print('words not in doc: ', kz)
        
            if len(kz) > 0:
                docKE += 1
            #input()

            f2 = open(pathList[3]+ '/' +f, 'w')
            f2.write('Words in Document:')
            for x in bwords:
                f2.write(x + ', ')
            
            f2.write('\nWords in Abstract:')
            for x in awords:
                f2.write(x + ', ')
            
            f2.write('\nWords in Abstract but not in Document:')
            for x in z:
                f2.write(x + ', ')
            
            f2.write('\nWords in Keyphrases:')
            for x in kewords:
                f2.write(x + ', ')
            
            f2.write('\nWords in Keyphrases but not in Document:')
            for x in kz:
                f2.write(x + ', ')
            
            f2.close()
            
        print('Total Document: ', docI)
        print('Total Abs - Document: ', docA)
        print('Total KE - Document: ', docKE)


    def get_wordnet_pos(self, treebank_tag):
    
    
        if treebank_tag.startswith('N'):
            return wn.NOUN
        elif treebank_tag.startswith('J'):
            return wn.ADJ
        elif treebank_tag.startswith('R'):
            return wn.ADV
        else:
            return ''





    def splitWords(self, lines):
       
        wordSet = set()
        for sid, s in enumerate(lines):
            s = s.rstrip('\n')
            s = s.lower()
            tokens = nltk.word_tokenize(s.translate(string.punctuation))
            tags = nltk.pos_tag(tokens)
            for ws in tags:
                z = ws[0].rstrip('\'\"-,.:;!?()[]{}\+')
                z = z.lstrip('\'\"-,.:;!?()[]{}\+')
                if len(z) > 0:
                    if ws[0] not in self.excludeSet:
                      w = z.lower()
                      w = self.stemmer.stem(w)
                      #pos = ws[1]
                      #poswn = self.get_wordnet_pos(pos)
                      #if poswn: #do not accept anything otherthan nouns
                      #myWord = str(self.lmtzr.lemmatize(w, poswn))
                      if w not in wordSet:
                                wordSet.add(w)
        return wordSet






    def splitKeywords(self, kelines):
        kelines = kelines.rstrip()
        words = re.findall(r'[\w]+', kelines)
        return words

def createDirs(wPathList):
    
    for w in wPathList:
        try:
            os.stat(w)
        except:
            os.mkdir(w)



def main():
    
    #set as default values
    readPath = '/Users/fahmidahamid/Desktop/ictir_2016/data/www_No_ABS'
    absPath = '/Users/fahmidahamid/Desktop/ictir_2016/data/www_ABS'
    kePath = '/Users/fahmidahamid/Desktop/ictir_2016/data/www_KE'
    writePathKES = '/Users/fahmidahamid/Desktop/ictir_2016/code/wwwSample_nonABS'
    #writePathKE = '/Users/fahmidahamid/Desktop/ictir_2016/code/wwwSample_nonKE'
                            
    createDirs([writePathKES])
    pathList = [absPath, kePath, readPath, writePathKES]
    print(pathList)
    db = nonDocBasedDataSet(pathList)

if __name__=="__main__":main()
