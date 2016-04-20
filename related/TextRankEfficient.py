#from __future__ import division
import os
import sys
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus.reader.plaintext import PlaintextCorpusReader
import nltk.tag
import string
import networkx as nx
from collections import defaultdict
import re
import math
import unicodedata

class Sample:
  name = ''
  pos = ''
  lemma_names = set()
  val = 0.0

class SentenceSample:
    ssen = ''
    weight = 0.000
    senIndex = 0
    
class overlapped :
    sen1 = ''
    sen2 = ''
    overLap = 0


class TextRank:
    
    def __init__(self):
        self.engStopWords = set(stopwords.words('english'))
        self.excludeSet = set(string.punctuation)
        self.tbl = dict.fromkeys(i for i in range(sys.maxunicode)
                if unicodedata.category(chr(i)).startswith('P'))
        self.lmtzr = WordNetLemmatizer()
        self.sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        tokenization_pattern = r'''(?x)([A-Z]\.)+| \w+(-\w+)*| \$?\d+(\.\d+)?%?| \w+[\x90-\xff]| [][.,;"'?():-_`]'''
        self.word_tokenizer = nltk.tokenize.regexp.RegexpTokenizer(tokenization_pattern)
    def findSimilarity(self, x,y):
    
    
        if(len(x) == 0 or len(y) == 0) :
           return 0
        else :
           z = x.intersection(y)
           weight = len(z)/ (len(x) + len(y) - len(z))
           return weight


    def get_wordnet_pos(self, treebank_tag):
    
        if treebank_tag.startswith('J'):
           return wn.ADJ
        elif treebank_tag.startswith('V'):
           return wn.VERB
        elif treebank_tag.startswith('N'):
           return wn.NOUN
        elif treebank_tag.startswith('R'):
           return wn.ADV
        else:
           return ''

    def buildGraph(self, sentences):

        g = nx.DiGraph()
        wordList = defaultdict()
        for sid, s in enumerate(sentences):
            print(sid, '>>', s)
            ids = set()
            y = s.lower()
            tokens = nltk.word_tokenize(y.translate(None, string.punctuation))
            #tokens = self.word_tokenizer(y)
            print(tokens)
            tags = nltk.pos_tag(tokens)
            wid = 0
            for ws in tags:
                if ws[0] not in self.engStopWords:
                   w = ws[0].lower()
                   pos = ws[1]
                   poswn = self.get_wordnet_pos(pos)
                   if poswn: #do not accept punctuations
                       myWord = self.lmtzr.lemmatize(w, poswn)
                       wsynset =  wn.synsets(myWord, poswn)
                       s1 = Sample()
                       word_id = str(wid) + '#'+str(sid)
                       s1.name = str(myWord)
                       if len(wsynset) > 0 :
                           wlemmas = wsynset[0].lemmas()
                           for wl in wlemmas:
                               s1.lemma_names.add(str(wl.name()))
                       s1.pos = poswn
                       wordList[word_id] = s1	#global
                       ids.add((word_id,s1)) #local --> for each sentence
                       g.add_node(s1.name, pos = s1.pos, rank = 0.001)
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
                        g.add_edge(x[1].name,y[1].name, weight = 0.0001)
                        g.add_edge(y[1].name, x[1].name, weight = 0.0001)
                        
        sz = g.number_of_edges()
        zs = float(1.0/float(sz))
        wordConsidered = set()
        for v1 in wordList.keys() :
           for v2 in wordList.keys() :
                if v1 != v2:
                    kv1 = wordList[v1]
                    kv2 = wordList[v2]
                    pair = (v1,v2)
                    pairr = (v2,v1)
                    if (pair not in wordConsidered) :
                        wordConsidered.add(pair)
                        wordConsidered.add(pairr)
                        set1 = kv1.lemma_names
                        set2 = kv2.lemma_names
                        similarity = self.findSimilarity(set1,set2)
                        if similarity > 0.000 :
                            if g.has_edge(kv1.name ,kv2.name) :
                                  g.edge[kv1.name][kv2.name]['weight'] += 0.0001 * similarity
                                  g.edge[kv2.name][kv1.name]['weight'] += 0.0001 * similarity
                            else :
                                  g.add_edge(kv1.name,kv2.name, weight = 0.0001 * similarity)
                                  g.add_edge(kv2.name, kv1.name, weight = 0.0001 * similarity)
    
    
        print(wordList)
        print(len(wordList))
        return g


    def applyTextRank(self, g):
    
        alpha = float(0.85)
        sz = g.number_of_edges()
        zs = float(1.0/float(sz))

        for i in range(1,100) :
            for n in g.nodes() :
                r = 0.000
                for p in g.predecessors(n) :
                    r += float(g.node[p]['rank']/g.out_degree(p))
                if(g.in_degree(n)!= 0) :
                    g.node[n]['rank'] = r * alpha + (1 - alpha) / float(g.number_of_nodes())


        highestR = -1.00
        lowestR = 1.00
        for n in g.nodes() :
            rank = g.node[n]['rank']
            print(n , 'rank :', g.node[n]['rank'],'\n')
            if highestR < rank and not math.isinf(rank) :
               highestR = rank
            if lowestR > rank and not math.isinf(rank) :
               lowestR = rank
        
        for n in g.nodes() :
           if g.node[n]['rank'] == float('inf') :
              g.node[n]['rank'] = highestR
           if g.node[n]['rank'] == float('-inf') :
              g.node[n]['rank'] = lowestR
           print(n ,'<new rank : ', g.node[n]['rank'],'>')
        
        
        return g



    def constructSentences(self, sentences, g, limit):
                  
        sentenceList = []
        g_nodes = g.number_of_nodes()
        index = 0
        for sindex, s in enumerate(sentences) :
            xs = SentenceSample()
            xs.ssen = s
            xs.senIndex = sindex
            
            s_weight = 0.00
            s_nodes = 0
            for n in s.split() :
                if n in g.nodes() :
                  s_weight += math.fabs(g.node[n]['rank'])
                  s_nodes += 1
            if s_nodes > 0 and s_weight > 0.00 :
                xs.matchId = (float)((total * g_nodes) /(totalNodes * totalWeight))
            else :
                xs.matchId = 0.00
            sentenceList.append(xs)
         
        
        sentenceList = sorted(sentenceList, key=lambda ps1: ps1.matchId, reverse = True)
        topSentences = sentenceList[:limit]
        topSentences = sorted(topSentences, key = lambda ps1: ps1.senIndex, reverse = False)
        return topSentences
                  
                  
                  
                  
    def writeSummary(self, summary_sentences, fname, outPath):
                  
        rem = open(outPath + '/' + fname, 'w')
        for s in summary_sentences:
            rem.write(s+'\n')
                  
        rem.close()
       
         
                  
                  

    def summarize(self, text, outPath, sum_size):
            sentences = nltk.sent_tokenize(text)
            g = self.buildGraph(sentences)
            g = self.applyTextRank(g)
            summary_sentences = self.constructSentences(sentences,g,sum_size)
            self.writeSummary(summary_sentences, fname, outPath)
        
