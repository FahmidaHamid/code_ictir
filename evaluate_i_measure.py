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

    def __init__(self, refSummPath, refKEPath, sysSummPath, sysKEPath, oPath, writePath, dataPath, ke, summ):
        self.refSummPath = refSummPath
        self.refKEPath = refKEPath
        self.sysSummPath = sysSummPath
        self.sysKEPath = sysKEPath
        self.writePath = writePath 
        self.oPath = oPath
        self.dataPath = dataPath
        self.ke = ke  #true or false
        self.summ = summ #true or false

        self.engStopWords = set(stopwords.words('english'))
        self.excludeSet = set(string.punctuation)
        self.excludeSet = self.excludeSet.union(self.engStopWords)
        extra = set(['also', 'e.g.', 'etc', 'et al.', 'et'])
        self.excludeSet = self.excludeSet.union(extra) 
        self.lmtzr = WordNetLemmatizer()




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

        wordList = dict()
        for sid, s in enumerate(sentences):
            s = s.rstrip('\n')
            s = s.lower()
            tokens = nltk.word_tokenize(s.translate(string.punctuation))   
            tags = nltk.pos_tag(tokens)
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
                        #lemma_names = set()
                        #if len(wsynset) > 0 :
                        #   wlemmas = wsynset[0].lemmas()
                        #   for wl in wlemmas:
                        #       lemma_names.add(str(wl.name()))
                        if myWord not in wordList:
                           wordList[myWord] = set(wsynset)	#global
        
        
        n = len(wordList.keys())
        
        return (n, wordList)

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
    
    def synset_score(self, ref_words, sw_synset):

        for r in ref_words.keys():
              if len(set(r).intersection(sw_synset)) > 0:
                 return (1, r)
              r_synset = ref_words[r]
              rzw = sw_synset.intersection(r_synset)
              if len(rzw) > 0:
                   return (1, r)
        return (0, None)




    def partialScores_synsets(self, zSet, ref_words, sys_words):

        partial_omega = 0
        partial_match = set()
        for sw in sys_words.keys():
            print(sw)
            if sw not in zSet:
               (x,y)= self.synset_score(ref_words, sys_words[sw])
               if x > 0:
                  partial_omega += 1
               if y is not None:
                  partial_match.add((sw,y))
        return (partial_omega, partial_match)





    def splitKeywords(self, keF):

         fopen = open(keF, 'r', errors='ignore')
         kelines = fopen.read() #read the keyphrases
         kelines = kelines.rstrip()
         fopen.close()
         words = re.findall(r'[\w]+', kelines)

         wordList = dict()
         
         for w in words:
             wsynset =  wn.synsets(w, 'n')
             if len(wsynset) > 0:
               wl_names = set(wn.synsets(w, 'n')[0].lemma_names())
               if w not in wordList:
                  wordList[w] = wl_names
             else:
                  wordList[w] = set()
         
         return (len(wordList.keys()), wordList)
         

    def writeSynsetData(self, f, localWords, ref_words, sys_words, complete_match, partial_match):
    
        data_file = open(self.dataPath + '/'+ f,  'w')
    
        data_file.write('Original Document:::\n-----------------------------\n')
        for x in localWords.keys():
            data_file.write(x + ':: '+ str(localWords[x]) + '\n')
        data_file.write('\nAbstract:::\n-----------------------------\n')
        for x in ref_words.keys():
            data_file.write(x + ':: '+ str(ref_words[x]) + '\n')
        data_file.write('\nTextRank Output:::\n-----------------------------\n')
        for x in sys_words.keys():
            data_file.write(x + ':: '+ str(sys_words[x]) + '\n')
        data_file.write('Completely Matched:\n------------------------------\n')
        for x in complete_match:
            data_file.write(x + '\n')
                            
        data_file.write('Partially Matched:\n----------------------------\n')
        for x in partial_match:
            data_file.write(x[0]+ '-->'+ x[1] + '\n')
        
        data_file.close()

    def writeData(self, fname, data):
        stat_file = open(self.writePath + '/'+ fname,  'w')
        stat_file.write('file_name *** n *** k *** l *** omega *** partial_omega ***rand_avg *** i_measure_o *** i_measure_p\n\n')
        
        for f in data:
            x = data[f]
            stat_file.write(f + ' *** ' + str(x[0])+ ' *** '+ str(x[1]) + ' *** ' + str(x[2]) + ' *** ' + str(x[3]) + ' *** '+ str(x[4]) +' *** ' + str(x[5]) + ' *** '+ str(x[6]) + ' *** ' + str(x[7])+'\n')
        
        
        
        stat_file.close()

    def iterOverAll(self, summ, ke):
      
      summStats = dict()
      keStats = dict()
      
      
      onlyfiles = [f for f in listdir(self.sysSummPath) if isfile(join(self.sysSummPath, f))]
        ##### read the entire file ####
      for f in onlyfiles:
            if f.startswith('.'):
               continue
            
            lines = self.readDataRaw(self.oPath, f) #read the body
            (local_n, localWords) = self.processData(lines)
            print('No of words in the document: ', local_n)
            if summ:
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
              partial = self.partialScores_synsets(zSet, ref_words, sys_words)
              print('Original Omega: ', local_omega)
              print('New Omega: ', local_omega + partial[0])
              (random_i, i_measure_v1) = self.i_measure(local_n, local_k, local_l, local_omega)
              (random_i, i_measure_v2) = self.i_measure(local_n, local_k, local_l, local_omega + partial[0])
              summStats[f] = (local_n, local_k, local_l, local_omega, partial[0],random_i, i_measure_v1, i_measure_v2)
            
              self.writeSynsetData(f, localWords, ref_words, sys_words, zSet, partial[1])
            if ke:
               (local_k, ref_words)= self.splitKeywords(self.refKEPath+'/'+f)
               if local_n == 0 or local_k == 0:
                  continue
               q = list(ref_words)
               (local_l, sys_words)= self.splitKeywords(self.sysKEPath+'/'+f)
               p = list(sys_words)
               zSet = self.x_and_y(p,q)
               print(zSet)
               local_omega = len(zSet)
               partial = self.partialScores_synsets(zSet, ref_words,sys_words)
               print('Original Omega: ', local_omega)
               print('New Omega: ', local_omega + partial[0])
               #input()
               (random_i, i_measure_v1) = self.i_measure(local_n, local_k, local_l, local_omega)
               (random_i, i_measure_v2) = self.i_measure(local_n, local_k, local_l, local_omega + partial[0])
                                         
               keStats[f] = (local_n, local_k, local_l, local_omega, partial[0], random_i, i_measure_v1, i_measure_v2)
    

      if summ:
           self.writeData('summ_stat.dat', summStats)
      if ke:
           self.writeData('ke_stat.dat', keStats)

#################################################################
#### reset the paths
#################################################################
readPath = '/Users/fahmidahamid/Desktop/ictir_2016/data/www_No_ABS'
absPath = '/Users/fahmidahamid/Desktop/ictir_2016/data/www_ABS'
kePath = '/Users/fahmidahamid/Desktop/ictir_2016/data/www_KE'
trPathSumm = '/Users/fahmidahamid/Desktop/ictir_2016/textrank_output/wwwSampleTextRank_Summ'
trPathKE = '/Users/fahmidahamid/Desktop/ictir_2016/textrank_output/wwwSampleTextRank_KE'
writePath = '/Users/fahmidahamid/Desktop/ictir_2016/code/www_result_stat'
dataPath = '/Users/fahmidahamid/Desktop/ictir_2016/code/synsetsApr28'
try:
    os.stat(writePath)
except:
    os.mkdir(writePath)       

try:
    os.stat(dataPath)
except:
    os.mkdir(dataPath)


evalTestCases = evaluate_i_measure(absPath, kePath, trPathSumm, trPathKE, readPath, writePath, dataPath, True, True)
evalTestCases.iterOverAll(True, True)

