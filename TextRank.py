#from __future__ import division
import os
import sys
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
import nltk.tag
import string
import networkx as nx
from collections import defaultdict
import re
import math
import unicodedata
import numpy

class Sample:
  name = ''
  lemma_names = set()
  
class SentenceSample:
    ssen = ''
    weight = 0.000
    senIndex = 0

class TextRank:
    
    def __init__(self, pathList):
        self.engStopWords = set(stopwords.words('english'))
        self.excludeSet = set(string.punctuation)
        self.excludeSet = self.excludeSet.union(self.engStopWords)
        extra = set(['also', 'e.g.', 'etc', 'et al.', 'et'])
        self.excludeSet = self.excludeSet.union(extra) 
        self.lmtzr = WordNetLemmatizer()
        self.stemmer = SnowballStemmer("english")
 
        self.readP = pathList[2]
        self.abstractP = pathList[0]
        self.keP = pathList[1]
        self.writeSumm = pathList[3] 
        if not os.path.exists(self.writeSumm):
           os.makedirs(self.writeSumm)        
        self.writeKE = pathList[4]
        if not os.path.exists(self.writeKE):
                  os.makedirs(self.writeKE)



    def findSimilarity(self, x,y):
    
    
        if(len(x) == 0 or len(y) == 0) :
           return 0
        else :
           z = x.intersection(y)
           weight = len(z)/ (len(x) + len(y) - len(z))
           return weight


    def get_wordnet_pos(self, treebank_tag):
    
        
        if treebank_tag.startswith('N'):
           return wn.NOUN
        elif treebank_tag.startswith('J'):
           return wn.ADJ
        elif treebank_tag.startswith('R'):
           return wn.ADV
        else:
           return ''

    def buildGraph(self, sentences):

        g = nx.DiGraph()
        wordList = defaultdict(set)
        for sid, s in enumerate(sentences):
            s = s.rstrip('\n')
            #print(sid, '>>', s)
            ids = set()
            s = s.lower()
            #tokens = nltk.word_from nltk.stem.porter import *tokenize(s.translate(self.tbl))
            tokens = nltk.word_tokenize(s.translate(string.punctuation))   
            tags = nltk.pos_tag(tokens)
            print(tags)
            wid = 0
            for ws in tags:
                z = ws[0].rstrip('\'\"-,.:;!?()[]{}\+')
                z = z.lstrip('\'\"-,.:;!?()[]{}\+') 
                if len(z) > 0:  
                   if ws[0] not in self.excludeSet:
                     w = z.lower()
                     pos = ws[1]
                     poswn = self.get_wordnet_pos(pos)
                     if poswn: #do not accept anything otherthan nouns
                        
                       myWord = self.lmtzr.lemmatize(w, poswn)
                       wsynset =  wn.synsets(myWord, poswn)                     
                       s1 = Sample()
                       word_id = str(wid) + '#'+str(sid)
                       s1.name = str(myWord)
                       if len(wsynset) > 0 :
                           wlemmas = wsynset[0].lemmas()
                           for wl in wlemmas:
                               s1.lemma_names.add(str(wl.name()))
                           #print(s1.lemma_names)
                       if s1.name not in wordList:
                            wordList[s1.name] = s1.lemma_names	#global
                       ids.add((word_id,s1)) #local --> for each sentence
                       g.add_node(s1.name)
                       wid += 1
        
            windowRange = 4
            for x in ids :
                for y in ids :
                   if x[0] != y[0] : # not the same word
                      idx = x[0]
                      idy = y[0]
                      partx = x[0].split('#')
                      party = y[0].split('#')
                      if abs(int(partx[0]) - int(party[0])) < windowRange :
                        g.add_edge(x[1].name,y[1].name, weight = 0.01)
                        g.add_edge(y[1].name, x[1].name, weight = 0.01)
                        
        sz = g.number_of_edges()
        if sz == 0:
             zs = 0
        else:   
             zs = float(1.0/float(sz))
        wordConsidered = set()
        for v1 in wordList.keys() :
           for v2 in wordList.keys() :
                if v1 != v2:
                    set1 = wordList[v1]
                    set2 = wordList[v2]
                    pair = (v1,v2)
                    pairr = (v2,v1)
                    if (pair not in wordConsidered) :
                        wordConsidered.add(pair)
                        wordConsidered.add(pairr)
                        similarity = self.findSimilarity(set1,set2)
                        if similarity > 0.000 :
                            if g.has_edge(v1,v2) :
                                  g.edge[v1][v2]['weight'] += zs * similarity
                                  g.edge[v2][v1]['weight'] += zs * similarity
                            else :
                                  g.add_edge(v1,v2, weight = zs * similarity)
                                  g.add_edge(v2, v1, weight = zs * similarity)
    
    
        #print(wordList)
        #print(len(wordList))
        #print(g.number_of_nodes())   
        return (g, len(wordList))


    def applyTextRank(self, g):
    
        pr = nx.pagerank_scipy(g, alpha=0.85, max_iter=100000, weight = 'weight')
        return pr



    def constructSentences(self, sentences, pg, limit):
                  
        sentenceList = []
        #words = sorted(pg.items(), key= lambda x: x[1], reverse=True)
        totalWeight = 0.00
        for w in pg:
            totalWeight += pg[w]
        g_nodes = len(pg.keys())
        #print(' Total Weight:: ', totalWeight)
        #print(' Total Nodes:: ', g_nodes)  
       
        for sindex, s in enumerate(sentences) :
            xs = SentenceSample()
            xs.ssen = s
            xs.senIndex = sindex
            
            s_weight = 0.00
            s_nodes = 0
            s =s.lower()
            tokens = nltk.word_tokenize(s.translate(string.punctuation))   
            
            for n in tokens :
                z = n.rstrip('\'\"-,.:;!?()[]{}\+')
                z = z.lstrip('\'\"-,.:;!?()[]{}\+')    
                if z in pg.keys() :
                  s_weight += math.fabs(pg[z])
                  s_nodes += 1
            if s_nodes > 0 and s_weight > 0.00 :
                xs.matchId = (s_weight * float(g_nodes)) / ( float(s_nodes) * totalWeight)
               # xs.matchId = s_weight / float(s_nodes)
            else :
                xs.matchId = 0.00
            
            sentenceList.append(xs)
         
        
        sentenceList = sorted(sentenceList, key=lambda ps1: ps1.matchId, reverse = True)
        topSentences = sentenceList[:limit]
        topSentences = sorted(topSentences, key = lambda ps1: ps1.senIndex, reverse = False)
        ss = ''
        for t in topSentences:
             t.ssen = t.ssen.rstrip('\n')
             ss = ss + ' ' + t.ssen.lower() 
        return (topSentences, ss)



    def getLemmas(self, setA):

        setB = set()
        stemmer = SnowballStemmer("english")
        setA = set(setA).difference(self.excludeSet)   
        for a in setA:
            print(a)
            xss = re.split(r'-', a)
            
            if len(xss) > 1:
               #input()
               #print(xss) 
               for xs in xss:
                   setB.add(stemmer.stem(xs))
            else:     
               setB.add(stemmer.stem(a))
        return setB          
    
    '''
    def compareAbstract(self, summary_sentences, abs_sentences, n, fname):

         precision = 0
         recall = 0
         avgO = 0
         i = 0
         i_measure = 0 
         #print('Abstract of ', fname) 
         tokens = set(nltk.word_tokenize(abs_sentences.translate(string.punctuation)))   
         tokens = tokens.difference(self.excludeSet)
         atokens = self.getLemmas(tokens)
         #print(atokens)   
         k = len(atokens)  
         trTokens = set(nltk.word_tokenize(summary_sentences.translate(string.punctuation)))
         trTokens = trTokens.difference(self.excludeSet)
         atrTokens = self.getLemmas(trTokens)     
         #print(atrTokens)
         l = len(atrTokens)
         AB = atokens.intersection(atrTokens)
         #print(AB) 
         i = len(AB)
         if n > 0: 
           precision = float(i)/float(l)
           recall = float(i)/float(k)
           avg_random = float(float(k * l) / float( n ))
           i_measure = float(i)/ avg_random
           print('P: ', precision, ' R: ', recall, ' i_measure: ', i_measure) 
           return (precision,recall,n,k,l, avg_random, i, i_measure)
         else:
           return (0,0,0,0,0,0,0,0)      
                  
    '''              
    def writeSummary(self, summary_sentences, pr, fname):
      
        rem = open(self.writeSumm + '/' + fname, 'w')
        rem.write(summary_sentences)
        rem.close()        

        #pfname = fname.rsplit('.txt', 1)[0] + '.pdf'          
        #os.system('cp '+ self.pdfP +'/'+ pfname + ' ' +  dir + '/'+ pfname)
        #os.system('cp ' + self.fileP +'/' + fname + ' ' + dir + '/' + fname.rsplit('.txt', 1)[0]+'_FULLTEXT.txt')       
        #os.system('cp ' + self.abstractP +'/' + fname + ' ' + dir + '/' + fname.rsplit('.txt', 1)[0]+'_ABSTRACT.txt') 
        #os.system('cp ' + self.keP +'/' + fname + ' ' + dir + '/' + fname.rsplit('.txt', 1)[0]+'_KE.txt')          
        #os.system('cp ' + self.readP +'/' + fname + ' ' + dir + '/' + fname.rsplit('.txt', 1)[0]+'_NO_ABS.txt')
        
        #rem = open(dir+'/summary_statistics.txt', 'w')
        #rem.write('Precision:: '+ str(round(tuple[0],2))+'\n')  
        #rem.write('Recall:: '+ str(round(tuple[1],2))+'\n')  
        #rem.write('Total Words :: '+ str(round(tuple[2],2)) + '\n')  
        #rem.write('Words in Abstract:: '+ str(round(tuple[3],2))+'\n')  
        #rem.write('Words in TR_Abs:: '+ str(round(tuple[4],2))+'\n')  
        #rem.write('Random_Avg_Overlap:: '+ str(round(tuple[5],2))+'\n')  
        #rem.write('Observed_Overlap:: '+ str(round(tuple[6],2))+'\n')
        #rem.write('i-measure:: '+ str(round(tuple[7],2))+'\n')  
          
        #rem.close()
          

    def trKES(self,fname, sum_size, sentences, abslines,gold_key_words): 
         #stats = dict()  
         (g,n) = self.buildGraph(sentences)
         pg = self.applyTextRank(g)
         self.summarize(fname, sum_size, sentences, abslines, pg,n)  
         self.findTopWords(fname, sentences, gold_key_words, pg,n)
         #return stats[fname]

    def summarize(self, fname, sum_size, sentences, abslines, pg,n):
            #myStats = dict()
            absSentences = nltk.sent_tokenize(abslines)
            if sum_size == 0:
                sum_size = len(absSentences)
            (summary_sentences, ss) = self.constructSentences(sentences,pg,sum_size)
            #self.compareAbstract(ss, abslines, n, fname)
            self.writeSummary(ss,pg, fname)
            print('Text Rank Summary:: ', ss)
            print('Original Abstract:: ', abslines)
            #print(sum_size)
            #input()
            #return myStats[fname] 
            

    
    def findTopWords(self, fname, sentences, gold_key_words, pg,n):
 

            #(g,n) = self.buildGraph(sentences)
            #pg = self.applyTextRank(g)
              
            sortedPG = sorted(pg.items(), key = lambda x: x[1], reverse = True)            
            
          
            goldWords = self.getLemmas(gold_key_words)
            print(goldWords)
            #input()
            k = len(goldWords)            
            rangeList = sorted([5, 10, 15, k])

            rem = open(self.writeKE + '/' + fname , 'w')
            for l in range(0, rangeList[3]):
                if l < len(sortedPG):
                   w = sortedPG[l][0]
                   if w not in self.excludeSet:  
                      rem.write( w + '\n')

            rem.close()

            #rem = open(dir + '/' + 'ke_statistics.txt' , 'w') 
            #rem.write('precision # recall # f-measure\nn #  k #  l # avg_random_intersection #  observed_intersection # i-measure\n')
            '''
            for l in rangeList:
                topWords = sortedPG[:l]
                topWordsOnly = [x[0] for x in topWords]
                trTopWords = self.getLemmas(topWordsOnly)
                print(trTopWords)  
                #input()
                AB = trTopWords.intersection(goldWords)     
                i = len(AB)
                if n > 0 and k > 0 and l > 0:
                   precision = float(i) /  float(l)
                   recall = float(i)/float(k)
                   if precision > 0.00 or recall > 0.00 :
                       f_measure = 2 * (precision * recall) / (precision + recall)
                   else:
                       f_measure = 0.00 
                   random_avg_intersection = float(k * l) / float(n)   
                   i_measure =  float(i) / random_avg_intersection 
                   rem.write('.......................................................................\n')
                   rem.write( str(round(precision, 2)) + ' ' +  str(round(recall, 2)) +' '+str(round(f_measure, 2)) + '\n')
                   rem.write(str(n) + ' ' + str(k) + ' '+ str(l) +' ' + str(round(random_avg_intersection, 2))+' ' + str(round(i_measure, 2)) +'\n')             
            
            

            rem.close()
            '''
