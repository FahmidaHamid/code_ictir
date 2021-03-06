from os import listdir
from os.path import isfile, join
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import sent_tokenize
import nltk
import string
import enchant
import chardet
import re
import os

def checkWords(rawData):


    d = enchant.Dict("en_US")
      
    rawData = re.sub(r'[^\x00-\x7F]+', ' ', rawData)
    num_format = re.compile("^[\-]?[1-9][0-9]*\.?[0-9]+$") 
    xData = rawData.split(' ')
    #print(xData)
    for i,x in enumerate(xData):
       try:
          encoding = x.encode("ascii")
       except UnicodeEncodeError:
          continue
       
       else:
          encoding = encoding.decode("ascii")            
       if encoding == x:           
           isnumber = re.match(num_format, x)
           if '-' in x and not isnumber:
               print(x)
                
               y = re.sub('-','',x)
               z = y.rstrip('\'\"-,.:;!?()[]{}')
               z = z.lstrip('\'\"-,.:;!?()[]{}')
               p = False   
               print(z)
               if len(z) > 0:
                  try:
                   p =  d.check(z)
                
                  except  Exception:
                      pass
                  if p:
                     xData[i] = y  
                     print(x, 'is changed to', y)
                    
    rData = [' '. join(x for x in xData)]
    return rData 


def adjustString(s, e, lines, prefix, stopEmpty):

    hyphenT = False
    mergedLines = ''
   
    for i in range(s,e):
       l = lines[i]
       l = l.rstrip()
       print(l)
       if len(l) == 0:
          print('empty line')
          if not stopEmpty:
             continue
          else:
             break   
       else:
          #input()
          if hyphenT:
                  mergedLines = mergedLines.rstrip() + l
          else:
                  mergedLines = mergedLines + ' ' + l 
               
          if l.endswith('-'): 
               hyphenT = True
               
          else:
               hyphenT = False
    print(mergedLines)
       
    mergedLines = mergedLines.lower()
    mergedLines = mergedLines.lstrip()
    mergedLines = mergedLines.rstrip()
    prefix = prefix.lower()
    if mergedLines.startswith(prefix):
       print(prefix)
       mergedLines = mergedLines[len(prefix):]
       pattern = re.compile(r'\n+')
       pattern2 = re.compile(r':') 
       mergedLines = re.sub(pattern, '', mergedLines)
       mergedLines = re.sub(pattern2, '', mergedLines)
       mergedLines = mergedLines.strip()
       l = checkWords(mergedLines) 
       #myLines = re.split('\n,\*;:', mergedLines)
     
       #for m in myLines:
       #    m = m.lstrip('\n')    
       #print(myLines)
       #input()
       mergedLines = l[0] 
    return mergedLines           




def parse(fname, ftitle, fabs, fnoabs, fke, fref):

    fopen = open(fname, 'r', errors='ignore')
    lines = fopen.readlines()
    fopen.close()
    myLines = []
    sentences = []
    sectionNames = []
    signature = 'WWW'
    hyphenT = False
    end = False
    j = 0
    tokenizer = RegexpTokenizer('\w+|\S+')
    
    begin_abs = -1  
    end_abs = -1
    
    begin_ke = -1
    end_ke = -1
    
    begin_title = 0
    end_title = -1
    
    begin_body = -1
    end_body = -1
 
    begin_ref = -1
    end_ref = -1 

    for l in lines:
        
       if 'ABSTRACT' in l:
           begin_abs = j
       if 'Categories and Subject Descriptors' in l and end_abs == -1:
           end_abs = j
       if 'General Terms' in l and end_abs == -1:
           end_abs = j
       if 'keywords' in l.lower() and end_abs != -1 and begin_ke == -1:
           begin_ke = j
       if 'INTRODUCTION' in l:
           end_ke = j 
           break
       j += 1
    absLines = adjustString(begin_abs, end_abs , lines, 'ABSTRACT', False)
    titleLines = adjustString(begin_title, begin_title+ 3, lines,'', True)
    wfile = open(ftitle, 'w')
    if len(titleLines) == 0:
       titleLines = adjustString(begin_title, begin_title+ 3, lines,'', False)
 
    wfile.write(titleLines + '\n')
    wfile.close()
    wfile = open(fabs, 'w') 
    wfile.write( absLines + '\n')
    wfile.close()

    keLines = adjustString(begin_ke, end_ke, lines, 'keywords', True)
    
    wfile = open(fke, 'w')
    wfile.write( keLines + '\n')
    wfile.close()

    begin_body = j+1
    myLines = []
    temp = ''
    for i in range(j+1, len(lines)):
        l = lines[i]
        if 'REFERENCES' in l: 
              end_body = i-1
              begin_ref = i     
              break
        if 'ACKNOWLEDGEMENTS' in l or 'Acknowledgements' in l:
           if end_body == -1:
              myLines.append(temp)
              temp = ''
              end_body = i-1
        else:
           l = l.rstrip()
           l = l.lstrip()
           if len(l) > 0 :
                #print('Current Line:: ', l)
                if l.startswith(signature):
                   continue
                elif re.match("^[0-9]+", l):
                   if l.isupper():
                       sectionNames.append(l)
                       temp += '\n'
                   if not l.islower():
                       sectionNames.append(l)
                       temp += '\n'
                   else:
                       if hyphenT:
                        temp += l
                        hyphenT = False
                       else: 
                        temp = temp + ' ' + l
                         
                elif l.isupper():
                   sectionNames.append(l)
                   temp += '\n'
                   continue 
                elif l.endswith('.'):
                    if hyphenT:
                       temp += l
                       hyphenT = False
                    else:  
                       temp = temp + ' ' + l
                    myLines.append(temp)
                    temp = ''
                    end = True 
                elif l.endswith('-'):
                     if hyphenT:
                        temp += l
                     else:
                        temp = temp + ' ' + l       
                     hyphenT = True
                     end = False  
                else:
                     if hyphenT:
                        temp += l
                        hyphenT = False
                     else: 
                        temp = temp + ' ' + l
                     end = False
    #print(myLines)
    for ml in myLines:
        extra_abbreviations = ['dr', 'vs', 'mr', 'mrs','ms', 'prof', 'inc', 'i.e', 'eg', 'al', 'fig']
        sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        sentence_tokenizer._params.abbrev_types.update(extra_abbreviations)            
        xml = sentence_tokenizer.tokenize(ml)
        print(xml)
        for x in xml:
            print(x)
            x = re.sub(' +', ' ', x)
            x = x.lstrip()
            x = x.rstrip()
            y =  checkWords(x)  
            sentences.append(y[0])
            print(y)
        #input()    
        #print(len(xml))
        #xs = tokenizer.tokenize(ml)
        #print(xs)
            
    print(sentences)    
    print(len(sentences))
    
    wfile = open(fnoabs, 'w')
    for s in sentences:
        wfile.write(s+ '\n')
    wfile.close()
     
    
    wfile = open(fref, 'w')
    pattern  = re.compile("^(\[[0-9]+\])")           
    for k in range(begin_ref + 1 , len(lines)):
        if len(lines[k]) > 0:
           l = lines[k]
           l = l.rstrip()
           if re.match("^\[[0-9]+\]", l):
              try:
                 found = re.search('\"\W+\"', l).group(1)
                 print('found:: ', found)
              except AttributeError:
                 found = '' 
              #input()
              #wfile.write('\n') 
           wfile.write(l + '\n')
           
           print(l)
    wfile.close()       
    #input()
    

def createDirs(wPathList):

    for w in wPathList:
        try:
            os.stat(w)
        except:
            os.mkdir(w)       
 


if __name__ == '__main__':

     writePathNoABS = '/Users/fahmidahamid/Desktop/ictir_2016/data/www_No_ABS'
     writePathABS = '/Users/fahmidahamid/Desktop/ictir_2016/data/www_ABS'
     writePathTitle = '/Users/fahmidahamid/Desktop/ictir_2016/data/www_Title'
     writePathKE = '/Users/fahmidahamid/Desktop/ictir_2016/data/www_KE'
     writePathReferences = '/Users/fahmidahamid/Desktop/ictir_2016/data/www_References' 
     readPath = '/Users/fahmidahamid/Desktop/ictir_2016/data/wwwSampleDataSetOut'


     createDirs([writePathNoABS, writePathABS, writePathTitle, writePathKE, writePathReferences])

     
     onlyfiles = [f for f in listdir(readPath) if isfile(join(readPath, f))]
     i = 0
     for f in onlyfiles:
         if f.startswith('.'):
            continue 
         if 'poster' in f or 'welcome' in f:
            continue    
         print('Reading from: ', f)
         
         x = readPath+ '/' + f
         t = writePathTitle + '/'+f
         a = writePathABS + '/' + f 
         b = writePathNoABS + '/'+f
         ke = writePathKE + '/'+f
         ref = writePathReferences + '/'+f
         parse(x,t,a,b,ke,ref)
        

