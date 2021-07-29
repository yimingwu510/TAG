from gensim.models import Word2Vec
from gensim.models.phrases import Phrases,Phraser
from gensim import corpora
from collections import Counter
import os
import math
import numpy
from numpy import *
import jieba
import chardet
import codecs
import shutil
import re
import Levenshtein
from pyltp import SentenceSplitter,Segmentor,Postagger


#p(oword|iword)
def predict_prob(iword, oword, model):
    if iword in model.wv.vocab and oword in model.wv.vocab:
        iword_vec = model[iword]
        oword = model.wv.vocab[oword]
        oword_l = model.syn1[oword.point].T
        dot = numpy.dot(iword_vec, oword_l)
        lprob = -sum(numpy.logaddexp(0, -dot) + oword.code * dot)
        prob = math.exp(lprob)
        return prob
    else:
        return -1

def vec_sim(vec1,vec2,option):
    if option=='cosine':
        if linalg.norm(vec1) * linalg.norm(vec2)==0:
            return -1
        else:
            return dot(vec1, vec2) / (linalg.norm(vec1) * linalg.norm(vec2))

def word_sim(word1, word2, word2vec,option):
    if word1 in word2vec.wv.vocab:
        vec1=word2vec[word1]
    else:
        grams=word1.split('\t')
        #n=len(grams)
        vecs=[word2vec[gram] for gram in grams if gram in word2vec.wv.vocab]
        n=len(vecs)
        sum=0
        for vec in vecs:
            sum+=vec
        vec1=sum/n if n>0 else 0
    if word2 in word2vec.wv.vocab:
        vec2=word2vec[word2]
    else:
        grams=word2.split('\t')
        #n=len(grams)
        vecs=[word2vec[gram] for gram in grams if gram in word2vec.wv.vocab]
        n=len(vecs)
        sum=0
        for vec in vecs:
            sum+=vec
        vec2=sum/n if n>0 else 0
    return vec_sim(vec1,vec2,option)


def levenshtein_distance(word1,word2):
    w1 = ''.join(word1.split('\t'))
    w2 = ''.join(word2.split('\t'))
    return  Levenshtein.distance(w1, w2)

def LF1(word,seed_bw,threshold1,model):
    sim=0
    for bw in seed_bw:
        sim+=word_sim(bw, word, model, 'cosine')
    ave_sim=sim/len(seed_bw)
    if ave_sim>threshold1:
        return True
    else:
        return False

def LF2(word,seed_bw,a,b,threshold2,model):
    for bw in seed_bw:
        sim = a*word_sim(bw, word, model, 'cosine') +b/(levenshtein_distance(bw, word)+1)
        if sim>threshold2:
            return True
    return False

def LF3(word,seed_bw,threshold3,model):
    for bw in seed_bw:
        prob = predict_prob(bw, word, model)
        if prob > threshold3:
            return True
    return False

word2vec=Word2Vec.load('../models/words(5-13)_v1.word2vec')
seed_bw=set([line.rstrip() for line in open('../results/blackwords(5-9).txt',encoding='utf-8').readlines()])#|set([line.strip() for line in open('results/crawler_keywords.txt',encoding='utf-8').readlines()])
filter=set( open('../dicts/sougou.dict',encoding='utf-8').read().split())|\
        set( open('../dicts/common.dict',encoding='utf-8').read().split())|\
         set(open('../dicts/symbols.txt',encoding='utf-8').read().split())|\
        set( open('../dicts/highfreq_ecowords.txt',encoding='utf-8').read().split())|\
       set( open('../dicts/stopwords.txt',encoding='utf-8').read().split())|set( open('../results/white_words.txt',encoding='utf-8').read().split())

cover=seed_bw&filter
print('%d black words in filter words:%s'%(len(cover),' '.join(cover)))


#pred_blackwords=open('../results/LF2_pred_blackwords(10-11)1.txt','w',encoding='utf-8')
articles=open('../data/sentences(10-13)_stopwords_v1.txt',encoding='utf-8').read().split('\n\n')
num=len(articles)-1
words=set()
blackwords=set()

for i in range(num):
    sentences=articles[i].split('\n')[4:]
    for sentence in sentences:
        if len(sentence)>1:
            pairs=sentence.split('\t')
            for pair in pairs:
                if len(pair)>1:
                    word=pair.split('/')[0]
                    pos=pair.split('/')[1]
                    if pos in ['n','ni','nl','ns','nz','v','i','j'] or word in seed_bw :# m,a,nh
                        words.add(word)
word=words-filter

a = 1#0.63
b =0#0.37
threshold1=0.25
threshold2 = 0.8
threshold3=0.000005

for word in words:
    #if word not in word2vec.wv.vocab:
        #print('%s not in vocab' % word)
    flag=LF2(word,seed_bw,a,b,threshold2,word2vec)#LF3(word,seed_bw,threshold3,word2vec)#LF2(word,seed_bw,a,b,threshold2,word2vec)#LF3(word,seed_bw,threshold3,word2vec)#LF1(word,seed_bw,threshold1,word2vec)
    if flag:
         blackwords.add(word)

#for word in blackwords:
#    pred_blackwords.write(word+'\n')



print('%d articles,%d words,%d predicted blackwords'%(num,len(words),len(blackwords)))
all_bw=set([line.rstrip() for line in open('../results/formal_blackwords.txt',encoding='utf-8').readlines()])|set([line.rstrip() for line in open('../results/LF2_new_bw(10-13)_r1.txt',encoding='utf-8').readlines()])
new=open('../results/LF2_new_bw(10-13)_r1_b=0c=0.8.txt','w',encoding='utf-8')
new_bw=blackwords-all_bw
print('%d new blackwords:'%len(new_bw))
for bw in new_bw:
    new.write(bw+'\n')

'''
similar_bw=open('results/sim_seed_bw.txt','w',encoding='utf-8')
sim_bw=set()
for bw in seed_bw:
    if bw in word2vec.wv.vocab:
        similar_bw.write(bw+':\n')
        simwords=(set([word for word,sim in word2vec.most_similar(bw,topn=10)])-all_bw-filter)&words
        sim_bw=sim_bw|simwords
        for word in simwords:
            similar_bw.write(word+'\n')
        similar_bw.write('\n')
new_bw=sim_bw-all_bw
print('%d new bw:'%len(new_bw) )
print(new_bw)
'''