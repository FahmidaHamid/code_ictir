from os import listdir
from os.path import isfile, join
from TextRank import TextRank
import csv
import re
import os

class BuildTRBasedDataSet:

    def __init__(self, pathList, sLen):
    
       
        onlyfiles = [f for f in listdir(pathList[0]) if isfile(join(pathList[0], f))]
        tr = TextRank(pathList)
        
        #stats = dict()
        i = 0

        for f in onlyfiles:
            if f.startswith('.'):
               continue
            print('Reading from: ', f)
            x = pathList[2]+ '/' + f
            fopen = open(x, 'r', errors='ignore')
            lines = fopen.readlines() #read the body
            fopen.close()
       
            absF = pathList[0] + '/'+f 
            fopen = open(absF, 'r', errors='ignore')
            abslines = fopen.read() #read the abstracts
            fopen.close()
            

            keF = pathList[1] + '/'+f
            fopen = open(keF, 'r', errors='ignore')
            kelines = fopen.read() #read the keyphrases
            fopen.close()
            #print(kelines)
            #input()
            words = self.splitKeywords(kelines) 
            tr.trKES(f, sLen, lines, abslines, words)
            #stats[f] = tr.summarize(str(i),f, sLen, lines, abslines)
            #tr.findTopWords(str(i), f, lines, words)
            #input()
            i += 1
            if i == 500:
               break 
        '''
        #avg_precision, avg_recall, avg_n, avg_k, avg_l, avg_random_i, avg_observed_i, avg_i_measure
        avg_tup = [0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00]
        size = 0 #consider only non-zero entries => ignore empty files
        with open(pathList[6], 'w') as csvfile:
           fieldnames = ['precision', 'recall', 'n','k','l','random_intersection','observed_intersection','i_measure']
           writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
           headers = dict((n,n) for n in fieldnames )
           writer.writerow(headers)   
           for x in stats:
               tup = stats[x] 
               if tup[0] == 0.0 and tup[1] == 0.0 and tup[2] == 0.0 and tup[3] == 0.0 and tup[4] == 0.0:
                   continue
               else:
                   writer.writerow({'precision': round(tup[0],2), 'recall': round(tup[1],2), 'n': round(tup[2],2), 'k': round(tup[3],2), 'l': round(tup[4],2), 'random_intersection':round(tup[5],2), 'observed_intersection':round(tup[6],2), 'i_measure': round(tup[7],2)})
                   for i in range(0,len(tup)):
                       avg_tup[i] += tup[i]
                   size += 1
           for i in range(0, len(avg_tup)):
               avg_tup[i] /= size
           writer.writerow({'precision': round(avg_tup[0],2), 'recall': round(avg_tup[1],2), 'n': round(avg_tup[2],2), 'k': round(avg_tup[3],2), 'l': round(avg_tup[4],2), 'random_intersection':round(avg_tup[5],2), 'observed_intersection':round(avg_tup[6],2), 'i_measure': round(avg_tup[7],2)})
        ''' 
        
    def splitKeywords(self, kelines):
         kelines = kelines.rstrip()  
         words = re.findall(r'[\w]+', kelines)
         #print(words)
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
     fullFilePath = '/Users/fahmidahamid/Desktop/ictir_2016/data/wwwSampleDataSetOut'
     writePathSumm = '/Users/fahmidahamid/Desktop/ictir_2016/system/wwwSampleTextRank_Summ'
     writePathKE = '/Users/fahmidahamid/Desktop/ictir_2016/system/wwwSampleTextRank_KE'

     createDirs([writePathSumm, writePathKE])
    
     #statsFile = './statsData.csv'
     sum_size = 0
     pathList = [absPath, kePath, readPath, writePathSumm, writePathKE]
     print(pathList)
     db = BuildTRBasedDataSet(pathList,sum_size)

if __name__=="__main__":main()




      
