import numpy
import os
import re
import shutil
from pyltp import SentenceSplitter,Segmentor,Postagger
#import Levenshtein
from preprocess import *


articles=open('../data/sentences(5-9)_stopwords_v000.txt',encoding='utf-8').read().split('\n\n')
num=len(articles)-1
blackwords=set([line.strip() for line in open('test.txt',encoding='utf-8').readlines() if not line.startswith('#')])

unigrams=set()
bigrams=set()
trigrams=set()
squagrams=set()
missing=set()
for bw in blackwords:
    stop=0
    find=0
    for i in range(num):
        sentences=articles[i].split('\n')
        for sentence in sentences[4:]:
            words=[]
            if len(sentence)>1:
                pairs=sentence.split('\t')
                for pair in pairs:
                    if len(pair)>1:
                        word=pair.split('/')[0]
                        pos=pair.split('/')[1]
                        #if pos in ['n','ni','nl','ns','nz','nd','nh','v','j','b','ws','d','q']: # m,a,i?
                        words.append(word)#(''.join(word.split('_')))
            if bw in words:
                unigrams.add(bw)
                stop=1
            else:
                for j in range(0,len(words)-1):
                    if (words[j]+words[j+1]==bw):
                        new=words[j]+'\t'+words[j+1]
                        bigrams.add(new)
                        stop=1
                        continue
                if stop==0:
                    for j in range(0, len(words)-2):
                        if (words[j] + words[j + 1]+words[j + 2] == bw):
                            new = words[j] + '\t' + words[j + 1]+ '\t' + words[j + 2]
                            trigrams.add(new)
                            stop = 1
                            continue
                if stop==0:
                    for j in range(0, len(words)-3):
                        if (words[j] + words[j + 1]+words[j + 2]+words[j + 3]== bw):
                            new = words[j] + '\t' + words[j + 1] + '\t' + words[j + 2]+ '\t' + words[j + 3]
                            squagrams.add(new)
                            stop = 1
                            continue
            if stop == 1:
                continue
        if stop==1:
            continue
    if stop == 1:
        continue
    else:
        missing.add(bw)

with open('../results/added.txt','w',encoding='utf-8') as out:
    out.write('unigrams\n')
    for gram in unigrams:
        out.write(gram+'\n')
    out.write('bigrams\n')
    for gram in bigrams:
        out.write(gram+'\n')
    out.write('trigrams\n')
    for gram in trigrams:
        out.write(gram+'\n')
    out.write('squagrams\n')
    for gram in squagrams:
        out.write(gram+'\n')
    out.write('missing\n')
    for gram in missing:
        out.write(gram+'\n')


cover=len(unigrams)+len(bigrams)+len(trigrams)+len(squagrams)
print('%d blackwords in total'%len(blackwords))
print('cover %d blackwords:%d unigrams,%d bigrams,%d trigrams,%d squagrams'%(cover,len(unigrams),len(bigrams),len(trigrams),len(squagrams)))
print('missing %d blackwords '%len(missing))




