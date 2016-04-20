from os import listdir
from os.path import isfile, join
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import sent_tokenize
import string
import enchant
import chardet
import re



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

def parse(fname, fw, fwA, fwKE):

    fopen = open(fname, 'r', errors='ignore')
    lines = fopen.readlines()
    fopen.close()
    myLines = []
    sentences = []
    sectionNames = []
    signature = 'WWW 2012'   
    temp = ''
    hyphenT = False
    end = False
    j = 0
    tokenizer = RegexpTokenizer('\w+|\S+')
    begin_abs = -1  
    end_abs = -1
    begin_ke = -1
    end_ke = -1
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
    absLines = adjustString(begin_abs, end_abs, lines, 'ABSTRACT', False)
    
    wfile = open(fwA, 'w')
    wfile.write( absLines + '\n')
    wfile.close()

    keLines = adjustString(begin_ke, end_ke, lines, 'keywords', True)
    
    wfile = open(fwKE, 'w')
    wfile.write( keLines + '\n')
    wfile.close()


    for i in range(j+1, len(lines)):
        l = lines[i]
        if 'REFERENCES' in l or 'ACKNOWLEDGEMENTS' in l:
           if not end:
              myLines.append(temp)
              end = True  
           break
        else:
           l = l.rstrip()
           l = l.lstrip()
           if len(l) > 0 :
                print('Current Line:: ', l)
                if signature in l:
                   continue
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
          
        xml = sent_tokenize(ml)
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
    
    wfile = open(fw, 'w')
    for s in sentences:
        wfile.write(s+ '\n')
    wfile.close()
    

if __name__ == '__main__':

     writePath = '/home/fahmida/Desktop/newProject/wwwSampleWOABS'
     writePathA = '/home/fahmida/Desktop/newProject/wwwSampleABS'
     writePathKE = '/home/fahmida/Desktop/newProject/wwwSampleKE'
     readPath = '/home/fahmida/Desktop/newProject/wwwSampleDataSetOut'
     onlyfiles = [f for f in listdir(readPath) if isfile(join(readPath, f))]
     #i = 0
     for f in onlyfiles:
         if f.startswith('.'):
            continue 
         print('Reading from: ', f)
         
         x = readPath+ '/' + f
         y = writePath + '/'+f
         z = writePathA + '/' + f 
         ke = writePathKE + '/'+f
         parse(x,y,z,ke)
         #i += 1
         #if i == 50:
         #   break

