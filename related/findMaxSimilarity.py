from itertools import combinations
from nltk.corpus import wordnet as wn
from copy import deepcopy


def maxSimilarity(list1):

    allSyns = dict()
    for (word,p) in list1:
      
       x =  wn.synsets(word, pos = p)
       print(word, '>>', x)
       
       if len(x) > 0:
           allSyns[word]  = x[0]
       else:
           allSyns[word] = None
                    
       print(allSyns[word])
       #input()
    
    #allSyns2 = deepcopy(allSyns1)

    simWordDict = dict()
    pairList = [pair for pair in combinations(allSyns.keys(), 2)]
    print(pairList)
    
    for p in pairList:
        s1 = allSyns[p[0]]
        s2 = allSyns[p[1]]
        if s1 is not None and s2 is not None: 
          z = wn.wup_similarity(s1, s2)
          if z is None:
            z = 0.00  
        else:
          z = 0.00
        x = tuple((p[1],z)) 
        y = tuple((p[0],z)) 
        if p[0] in simWordDict.keys():
           simWordDict[p[0]].add(x)
      
        else:
          simWordDict[p[0]] = set([x])
        if p[1] in simWordDict.keys():
           simWordDict[p[1]].add(y)

        else:
          simWordDict[p[1]] = set([y])
  
    
    print(simWordDict)
    input()
    #sList = sorted(simWordDict.items(), key = lambda x: x[0])
    for k in simWordDict.keys():
        print(k)
        values = list(simWordDict[k])
        if len(values) > 0:
           svalues = sorted(values, key = lambda x: x[1], reverse = True)
           print(svalues)
        else:
           print(values)   


 
    print(len(pairList))
    print(len(simWordDict)) 
    


a = [('book','v'), ('pickle','n'),('play', 'v'), ('ball','n'),\
     ('article','n'), ('novel','n'), ('food','n'), ('eat','v'),\
     ('river','n'), ('bank','n'), ('money','n'), ('field','n'), \
     ('football','n'),('office','n'),('summer','n'), ('heat','n'), ('fire','n')]
maxSimilarity(a)
