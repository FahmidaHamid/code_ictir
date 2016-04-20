import sys
import os
import string
import re
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

    def __init__(self, refSummPath, refKEPath, sysSummPath, sysKEPath, oPath, writePath, ke, summ):
        self.refSummPath = refSummPath
        self.refKEPath = refKEPath
        self.sysSummPath = sysSummPath
        self.sysKEPath = sysKEPath
        self.writePath = writePath 
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
        if distance:
           return 1.0 / (distance + 1)
        else:
           return -1




    def i_measure(self, n,k,l,omega):
        if n > 0:       
           i = float(k * l) / float(n)
           if i > 0.00:
              i_measure_v = float(omega) / float(i)
           else:
              i_measure_v = 0.00  
           return (i, i_measure_v)
        else:
           return (0.00, 0.00) 


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
                       #wsynset =  wn.synsets(myWord, poswn)                     
                       if myWord not in lWord.keys():
                            lWord[myWord] = set([poswn])
                       else:
                            lWord[myWord].add(poswn)   

        
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

    def x_and_y(self,x,y): 
         
        xSet = set(x)
        ySet = set(y)

        zSet = ySet.intersection(xSet)

        return zSet
    
   
    def simScore(self, wTuple, ref_words):
    
        maxS = -1.00
        s1 = wn.synsets(wTuple[0], wTuple[1])
        if s1: 
           synset1 = s1[0] 
           for t in ref_words.keys():
             s2 = wn.synsets(t, ref_words[t])
             if s2 and synset1: 
               synset2 = s2[0]
               temp = self.path_similarity(synset1, synset2)
               if temp > maxS:
                  maxS = temp
        return maxS     

    def simScore_ke(self, w, ref_words):
    
        maxS = -1.00
        s1 = wn.synsets(w, 'n')
        if s1: 
           synset1 = s1[0] 
           for t in ref_words:
             s2 = wn.synsets(t, 'n')
             if s2 and synset1: 
               synset2 = s2[0]
               temp = self.path_similarity(synset1, synset2)
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
                 pscore = self.simScore((sw, sys_words[sw]), ref_words)
                 if pscore != -1:
                        itemScore[sw] = pscore
                        print(itemScore[sw])
        return itemScore 


    def partialScores_ke(self, zSet,ref_words, sys_words):

        itemScore = dict()

        for sw in sys_words:
            print(sw)
            if sw in zSet:
                 itemScore[sw] = 1.00
                 print(itemScore[sw])
            else:
                 pscore = self.simScore_ke(sw, ref_words)
                 if pscore != -1:
                        itemScore[sw] = pscore
                        print(itemScore[sw])
        return itemScore 




    def splitKeywords(self, keF):

         fopen = open(keF, 'r', errors='ignore')
         kelines = fopen.read() #read the keyphrases
         kelines = kelines.rstrip()
         fopen.close()
         words = re.findall(r'[\w]+', kelines)
         #print(words)
         return (len(words), words)   
         

         
    def iterOverAll(self, summ, ke):
         
      if summ:   
        onlyfiles = [f for f in listdir(self.sysSummPath) if isfile(join(self.sysSummPath, f))]
        fname = 'summary_score.dat'
        stat_file = open(self.writePath + '/'+ fname,  'w')
        stat_file.write('file_name *** n *** k *** l *** omega *** rand_avg *** i_measure *** score\n')
        ##### read the entire file ####
        for f in onlyfiles:
            if f.startswith('.'):
               continue
            
            lines = self.readDataRaw(self.oPath, f) #read the body
            (local_n, localWords) = self.processData(lines)
            print('No of words in the document: ', local_n) 
            absLines = self.readDataRaw(self.refSummPath, f)
            (local_k, ref_words) = self.processData(absLines)
            if local_n == 0 or local_k == 0:
                continue 
            q = list(ref_words.keys())
            sys_absLines = self.readDataRaw(self.sysSummPath, f)
            (local_l, sys_words) = self.processData(sys_absLines)
            p = list(sys_words.keys())
            zSet = self.x_and_y(p,q)
            local_omega = len(zSet)
            item_score = self.partialScores(zSet, ref_words, sys_words)   
            total_score = 0.00
            for z in item_score.keys():
                total_score += item_score[z]
            (random_i, i_measure_v) = self.i_measure(local_n, local_k, local_l, local_omega)
            if i_measure_v != 0 and total_score != 0:
                 score = i_measure_v * total_score
            else:
                 score = total_score
            stat_file.write(f + ' *** ' + str(local_n)+ ' *** '+ str(local_k) + ' *** ' + str(local_l) + ' *** ' + str(local_omega) + ' *** ' + str(random_i) + ' *** '+ str(i_measure_v) + ' *** ' + str(score)+ '\n')     
            print('Score:: ', score)
            
        stat_file.close()


        if ke:   
          onlyfiles = [f for f in listdir(self.sysKEPath) if isfile(join(self.sysKEPath, f))]
          fname = 'ke_score.dat'
          stat_file = open(self.writePath + '/'+ fname,  'w')
          stat_file.write('file_name *** n *** k *** l *** omega *** rand_avg *** i_measure *** score\n')
          ##### read the entire file ####
          for f in onlyfiles:
             if f.startswith('.'):
                continue
            
             lines = self.readDataRaw(self.oPath, f) #read the body
             (local_n, local_words) = self.processData(lines)
             print('No of words in the document: ', local_n) 
             (local_k, ref_words)= self.splitKeywords(self.refKEPath+'/'+f)
             if local_n == 0 or local_k == 0:
                continue 
             q = list(ref_words)
             (local_l, sys_words)= self.splitKeywords(self.sysKEPath+'/'+f)
             #print('No of words in system output: ', local_l)
             #input() 
             p = list(sys_words)
             zSet = self.x_and_y(p,q)
             print(zSet)
             local_omega = len(zSet)
             #input()  
             item_score = self.partialScores_ke(zSet, ref_words, sys_words)   
             #print(local_l)
             print(sys_words)
             print(ref_words)
             total_score = 0.00
             for z in item_score.keys():
                print(z, '>>', item_score[z])
                total_score += item_score[z]
             (random_i, i_measure_v) = self.i_measure(local_n, local_k, local_l, local_omega)
             if i_measure_v != 0 and total_score != 0:
                 score = i_measure_v * total_score
             else:
                 score = total_score
             stat_file.write(f + ' *** ' + str(local_n)+ ' *** '+ str(local_k) + ' *** ' + str(local_l) + ' *** ' + str(local_omega) + ' *** ' + str(random_i) + ' *** '+ str(i_measure_v) + ' *** ' + str(score)+ '\n')     
             print('Score:: ', score)
            
          stat_file.close()
   

#################################################################
#### reset the paths
#################################################################
readPath = '/Users/fahmidahamid/Desktop/ictir_2016/data/www_No_ABS'
absPath = '/Users/fahmidahamid/Desktop/ictir_2016/data/www_ABS'
kePath = '/Users/fahmidahamid/Desktop/ictir_2016/data/www_KE'
trPathSumm = '/Users/fahmidahamid/Desktop/ictir_2016/system/wwwSampleTextRank_Summ'
trPathKE = '/Users/fahmidahamid/Desktop/ictir_2016/system/wwwSampleTextRank_KE'
writePath = '/Users/fahmidahamid/Desktop/ictir_2016/system/www_result_stat'
try:
    os.stat(writePath)
except:
    os.mkdir(writePath)       

evalTestCases = evaluate_i_measure(absPath, kePath, trPathSumm, trPathKE, readPath, writePath, True, True)
evalTestCases.iterOverAll(True, True)

