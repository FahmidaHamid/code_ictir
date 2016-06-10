##### This is the README for the CODES ###########
1. /related:\\
     different versions of old codes to parse the text from PDFs
2./synsetsApr28:\\
    for each paper, the words along with their synsets (found in the wordnet)
                    found in the original paper, in the abstract, and in the textrank summary
                    at the end:
                        list of words that matches (exactly or through synset) between abstract and textrank summary
                        
3. /wwwSample_nonABS:\\
      for each file, list the words that are 
         a. in Document
         b. in Abstract
         c. in Abstract but not in Document
         d. in Author-written Keyphrases
         e. in Author-written Keyphrases but not in Document 

4. www_result_stat/:\\
        ke_stat.dat \\
           file_name *** n *** k *** l *** omega *** partial_omega ***rand_avg *** i_measure_o *** i_measure_p
        summ_stat.dat\\
           file_name *** n *** k *** l *** omega *** partial_omega ***rand_avg *** i_measure_o *** i_measure_p
4. stat.txt:\\
     count: 
       a. total files, 
       b. total files where some words in abstract are not in the document,
       c. total files where some of the author-written keyphrases are not in the original document 
5. TextRank.py\\

6. absIntersect.py \\
     to count the statistics written on "stats.txt" file
7.convertPDFs.py
     convert pdfs to raw text
8. evaluate_i_measure.py \\
     \\evaluate the textrank written output with the abstract( and/or keyphrases)
     \\and produce the ke_stat.dat and summ_stat.dat files
     \\if you do not want to evaluate the keyphrases, set the boolean values accordingly.
     \\For example, evalTestCases.iterOverAll(True, False) will only creat the summ_stat.dat file
     \\terminal instruction: python3 evaluate_i_measure.py 
9. parseDocument.py:\\
     parse the raw text to 5 separate files:
     \\a. abstract
     \\b. title
     \\c. author-written keyphrases
     \\d. body of the paper/article
     \\e. list of references  
