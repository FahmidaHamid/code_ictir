import sys
import os
import string
from os import listdir
import os.path
import nltk.tag
from os.path import isfile, join
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer


class evaluate_i_measure:

    def __init__(self, refSummPath, refKEPath, sysSummPath, sysKEPath, oPath, ke, summ):
        self.refSummPath = refSummPath
        self.refKEPath = refKEPath
        self.sysSummPath = sysSummPath
        self.sysKEPath = sysKEPath

        self.oPath = oPath
        self.ke = ke  #true or false
        self.summ = summ #true or false

        self.engStopWords = set(stopwords.words('english'))
        self.excludeSet = set(string.punctuation)
        self.excludeSet = self.excludeSet.union(self.engStopWords)
        extra = set(['also', 'e.g.', 'etc', 'et al.', 'et'])
        self.excludeSet = self.excludeSet.union(extra) 
        self.lmtzr = WordNetLemmatizer()


    def path_similarity(self,synset1, synset2):
    
        print('Synset1: ',synset1)
        print('Synset2: ',synset2)
        
        distance = synset1.shortest_path_distance(synset2)
        if distance >= 0:
           return 1.0 / (distance + 1)
        else:
           return -1




    def i_measure(self, n,k,l,omega):
       
        i =  float(n) / float(k * l)
        i_measure = float(omega) / float(i)
        return (i, i_measure)


    def get_wordnet_pos(self, treebank_tag):
    
        
        if treebank_tag.startswith('N'):
           return wn.NOUN
        elif treebank_tag.startswith('J'):
           return wn.ADJ
        elif treebank_tag.startswith('R'):
           return wn.ADV
        else:
           return ''



    def processData(self, sentences):

        lWord = dict()
        for sid, s in enumerate(sentences):
            s = s.rstrip('\n')
            s = s.lower()
            tokens = nltk.word_tokenize(s.translate(string.punctuation))   
            tags = nltk.pos_tag(tokens)
            #print(tags)
            for ws in tags:
                z = ws[0].rstrip('\'\"-,.:;!?()[]{}\+\\\/')
                z = z.lstrip('\'\"-,.:;!?()[]{}\+\\\/') 
                print(z)
                if len(z) > 0:  
                   if ws[0] not in self.excludeSet:
                     pos = ws[1]
                     poswn = self.get_wordnet_pos(pos)
                     if poswn: #do not accept anything otherthan nouns                        
                       myWord = self.lmtzr.lemmatize(z, poswn)
                       wsynset =  wn.synsets(myWord, poswn)                     
                       if (myWord, poswn) not in lWord.keys():
                            lWord[(myWord, poswn)] = wsynset

        
        n = len(lWord.keys())
        
        return (n, lWord)

    def readDataRaw(self, cpath, fname):
    
        x = cpath+ '/' + fname
        if os.path.exists(x):  
           fopen = open(x, 'r', errors='ignore')
           lines = fopen.readlines() #read the body
           fopen.close()
           return lines     
        else:
           return '' 

    def x_notin_y(self,x,y): 
         
        #print(x)
        #print(y)
        #input() 
        xSet = set([c[0] for c in x])
        ySet = set([c[0] for c in y])

        zSet = ySet.intersection(xSet)
        print(xSet)
        print(ySet)
        print(zSet)
        return zSet
    
   
    def simScore(self, s, ref_words):
    
        maxS = -1.00
        for w in ref_words.keys():
            temp = self.path_similarity(s, ref_words[w])
            if temp > maxS:
               maxS = temp
        return maxS     


    def partialScores(self, zSet,ref_words, sys_words):

        itemScore = dict()

        for sw in sys_words.keys():
            print(sw)
            if sw in zSet:
                 itemScore[sw] = 1.00
                 print(itemScore[sw])
            else:
                 pscore = self.simScore(sys_words[sw], ref_words)
                 if pscore != -1:
                        itemScore[sw] = pscore
                        print(itemScore[sw])
        return itemScore 
         

         
    def iterOverAll(self, summ):
         
           
        onlyfiles = [f for f in listdir(self.sysSummPath) if isfile(join(self.sysSummPath, f))]
        
        ##### read the entire file ####
        for f in onlyfiles:
            if f.startswith('.'):
               continue
            
            lines = self.readDataRaw(self.oPath, f) #read the body
            (local_n, localWords) = self.processData(lines)
            print(local_n) 
            print(localWords)
            #p = list(localWords) 
            absLines = self.readDataRaw(self.refSummPath, f)
            (local_k, ref_words) = self.processData(absLines)
            print(local_k)
            q = list(ref_words.keys())
            #zSet = self.x_notin_y(p,q) 
            sys_absLines = self.readDataRaw(self.sysSummPath, f)
            (local_l, sys_words) = self.processData(sys_absLines)
            p = list(sys_words.keys())
            zSet = self.x_notin_y(p,q)
            print(zSet)
            input()  
            item_score = self.partialScores(zSet, ref_words, sys_words)   
            print(local_l)
            print(sys_words.keys())
            for z in item_score.keys():
                print(z, '>>', item_score[z])
            input()     
            

   

#################################################################
#### reset the paths
#################################################################
readPath = '/home/fahmida/Desktop/newProject/exp2/www_No_ABS'
absPath = '/home/fahmida/Desktop/newProject/exp2/www_ABS'
kePath = '/home/fahmida/Desktop/newProject/exp2/www_KE'
trPathSumm = '/home/fahmida/Desktop/newProject/wwwSampleTextRank_Summ'
trPathKE = '/home/fahmida/Desktop/newProject/wwwSampleTextRank_KE'


evalTestCases = evaluate_i_measure(absPath, kePath, trPathSumm, trPathKE, readPath, True, True)
evalTestCases.iterOverAll(True)

