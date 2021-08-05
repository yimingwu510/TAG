from gensim.models import Word2Vec
from gensim.models.phrases import Phrases, Phraser
from gensim import corpora
from collections import Counter
import os
import math
import numpy
import jieba
import chardet
import codecs
import re
from pyltp import SentenceSplitter, Segmentor, Postagger


def cut_sentences(text,punts):
    start = 0
    i = 0     sentences = []
    for char in text:
        if char in punts:
            sentences.append(text[start:i+1])
            start = i + 1  
            i += 1
        else:
            i += 1  
    if start < len(text):
        sentences.append(text[start:])  
    return sentences

def cut_words(sentence, segmentor,filter=[]):
    urls = set()
    numbers = set()
    words = []
    # number = re.compile('(?:\+|-)?\d+\.?\d*%*')
    url1 = re.compile('https?://[a-zA-Z0-9?/&=:@%-.]+')
    url2 = re.compile('www\.[a-zA-Z0-9?/&=:@%-]+\.[a-zA-Z0-9?/&=:@%-.]+')
    url3 = re.compile('[a-zA-Z0-9?/&=:@%-.]+\.(?:com|net|cn|org|html)')
    for str in re.findall(url1, sentence, ):
        urls.add(str)
        sentence = sentence.replace(str, 'url')
    for str in re.findall(url2, sentence, ):
        urls.add(str)
        sentence = sentence.replace(str, 'url')
    for str in re.findall(url3, sentence):
        urls.add(str)
        sentence = sentence.replace(str, 'url')
        # for str in re.findall(number, sentence):
        # numbers.add(str)
        # sentence = sentence.replace(str, ' ')
    # temp = jieba.cut(sentence, cut_all=False)
    temp = segmentor.segment(sentence)
    for word in temp:
        if word not in filter:
            if word not in ['\t', '\n', ' ','']:
                words.append(word)
    return urls, numbers, words



filter = set( [line.strip() for line in open(‘../data/stopwords.txt',encoding='utf-8').readlines()])
punts='，；。？！,;?!'
segmentor = Segmentor()
segmentor.load_with_lexicon(‘../data/ltp-data-v3.4.0/cws.model’,’../data/all.dict')
postagger = Postagger()
postagger.load('../data/ltp-data-v3.4.0/pos.model')
#bigram=Phrases.load('models/phrases(5-9).bigram')
#trigram=Phrases.load('models/phrases(5-9).trigram')
#squagram=Phrases.load('models/phrases(5-9).squagram')

if __name__=="__main__":
    records = open(‘../data/dedup_records(10-13).txt', 'r', encoding='utf-8').read().split('\001')
    all_sentences=open('../data/sentences(10-13)_stopwords_v1.txt','w',encoding='utf-8')
    vocab=set()
    num = len(records) - 1
    sentence_num=0
    source2num={}
    month2num={}
    for i in range(num):
        tuple = records[i].split('||')
        id = tuple[0]
        description = tuple[2]
        crawler_keyword = tuple[3]
        source=tuple[4]
        pub_time_a = tuple[7]
        date = pub_time_a.split(' ')[0]
        month=date.split('-')[1]
        date = ''.join(date.split('-'))
        all_sentences.write(id+'\n')
        all_sentences.write(date + '\n')
        all_sentences.write(source+'\n')
        all_sentences.write(crawler_keyword+ '\n')
        sentences = cut_sentences(description,punts)

        for sentence in sentences:
            urls, numbers, words = cut_words(sentence,segmentor,filter)
            sentence=words#trigram[bigram[words]]#
            #sentence = [''.join(word.split('_')) for word in sentence]
            if len(sentence)>=1:
                postags = postagger.postag(sentence)
                if len(sentence) == len(postags):  # meaningless sentence can not be pos-tagged
                    try:
                        source2num[source] = source2num[source] + 1  # + len(sentences)
                    except KeyError:
                        source2num[source] = 1
                    try:
                        month2num[month] = month2num[month] + 1  # + len(sentences)
                    except KeyError:
                        month2num[month] = 1
                    sentence_num += 1
                    i = 0
                    for word in sentence:
                        vocab.add(word)
                        all_sentences.write(word + '/' + postags[i] + '\t')
                        i+=1
                    all_sentences.write('\n')
        all_sentences.write('\n')

    seed_blackwords =set([ line.strip() for line in open('../results/seed_blackwords_v0.txt', 'r', encoding='utf-8').readlines()])
    cover=vocab&seed_blackwords
    missing=seed_blackwords-cover
    coverage=len(cover)/len(seed_blackwords)
    print('%d articles,%d sentences'%(num,sentence_num))
    n=0
    for source in source2num:
        n+=source2num[source]
        print('%d sentences from %s'%(source2num[source],source))
    print('%d sentences in total' % n)
    n=0
    for month in month2num:
        n+=month2num[month]
        print('%d sentences from %s'%(month2num[month],month))
    print('%d sentences in total'%n)
    print('%d vocab,covering %s seed blackwords'%(len(vocab),coverage))
    print('missing seed blackwords: '+' '.join(missing))



  
