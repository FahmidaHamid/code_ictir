from os import listdir
from os.path import isfile, join
import os

readPath = '/Users/fahmidahamid/Desktop/ictir_2016/data/wwwSampleDataSet'
writePath = '/Users/fahmidahamid/Desktop/ictir_2016/data/wwwSampleDataSetOut'

try:
    os.stat(writePath)
except:
    os.mkdir(writePath)       


#os.system('pdf2txt.py /Users/fahmida/Downloads/pdfminer-master/samples/simple1.pdf')

onlyfiles = [f for f in listdir(readPath) if isfile(join(readPath, f))]

print(onlyfiles)

for f in onlyfiles:
    f2 = f
    f2 = f2.replace('.pdf', '.txt')
    print('Original File: ', f)
    print('Converted File: ', f2)
    x = readPath+ '/' + f
    print(x)
    y = writePath + '/'+ f2
    print(y)
    cmd = 'pdf2txt.py ' + x + '>' + y  
    os.system(cmd)
