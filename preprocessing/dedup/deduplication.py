from pysimhash.hashes.simhash import simhash
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from numpy import *
import os
import re
import sys
import codecs
import chardet
import shutil
import jieba
import time
from pyltp import SentenceSplitter,Segmentor,Postagger


def cut_words(sentence, filter):
    urls = set()
    numbers=set()
    words = []
    number = re.compile('(?:\+|-)?\d+\.?\d*%*')
    url1 = re.compile('https?://[a-zA-Z0-9/&=:?#@%-_.]+')
    url2 = re.compile('www\.[a-zA-Z0-9/&=:?#@%-_]+\.[a-zA-Z0-9/&=:?#@%-_]+\.[a-zA-Z0-9/&=:?#@%-_.]+')
    url3=re.compile('[a-zA-Z0-9/&=:?#@%_.-]+(?:com|net|cn|org)')
    for str in re.findall(url1, sentence,):
        urls.add(str)
        sentence = sentence.replace(str, ' ')
    for str in re.findall(url2, sentence,):
        urls.add(str)
        sentence = sentence.replace(str, ' ')
    for str in re.findall(url3, sentence):
        urls.add(str)
        sentence = sentence.replace(str, ' ')
    for str in re.findall(number, sentence):
        numbers.add(str)
        sentence = sentence.replace(str, ' ')
    temp = segmentor.segment(sentence)#segmentor.segment(sentence)#jieba.cut(sentence,cut_all=False)#
    for word in temp:
        if word not in filter:
            if word not in ['\n','\t',' ']:
                words.append(word)
    return urls,numbers,words

def text_filter(text):
    pat1 = re.compile('[a-zA-Z0-9 ,.:;"!/@#$%&*+=_~(){}<>\\\^\-\?\[\]\']{50,1000}[; ]')
    pat2 = re.compile('(&lt;)(.*?)(&gt;)')
    pat3 = re.compile('<[^>]+>')
    pat4 = re.compile('(&img)*(&amp)*(&gt)*(&lt)*(&times)*(&nbsp)*(&quot)*(&middot)*(/p)*')
    pat5 = '[[+_+]]'
    pat6 = '\\n'
    a1 = re.sub(pat1, '', text)
    a2 = re.sub(pat2, '', a1)
    a3 = re.sub(pat3, '', a2)
    a4 = re.sub(pat4, '', a3)
    a5 = a4.replace(pat5, '')
    a6 = a5.replace(pat6, '')
    return a6

filter=set( [line.strip() for line in open(‘../data/stopwords.txt',encoding='utf-8').readlines()])
segmentor = Segmentor()
segmentor.load_with_lexicon(‘../data/ltp-data-v3.3.1/cws.model’,’../data/seed_blackwords.txt')

sim_threshold=0.98
hashbits = 64
before_dedup_1 =open( ‘../data/records(5-9).txt','r',encoding='utf-8')
before_dedup_2 =open( ‘../data/records(10-13).txt','r',encoding='utf-8')
dedup_records = open(‘../data/dedup_records(5-13)_new.txt','w',encoding='utf-8')

part1=before_dedup_1.read()
part2=before_dedup_2.read()
records_dict={}
corpus_dict={}
hashes=[]
all_urls=set()


start_time=time.time()
i=0
for part in [part1,part2]:
    records=part.split('\001')
    print('!!!!',len(records))
    for record in records:
        tuple=record.split('||')
        if len(tuple)==8:
            id = tuple[0]

            if id=='3843998822':
                continue

            i+=1
            print('%d articles loaded'%i)
            pub_time_a = tuple[7]
            date = pub_time_a.split(' ')[0]
            year, month, day = date.split('-')
            date =int( ''.join([year, month, day]))

            referer_url=tuple[1]
            description=tuple[2]
            crawler_keyword=tuple[3]
            source=tuple[4]
            groupid=tuple[5]
            abstract=tuple[6]
            description=' '.join(description.split())
            description=text_filter(description)
            urls, numbers,words = cut_words(description, filter)
            all_urls=all_urls|urls

            hash = simhash(words, hashbits=hashbits)
            new_records = id + '||' + referer_url + '||' + description + '||' + crawler_keyword + '||' + source + '||' + groupid + '||' + abstract + '||' + pub_time_a

            try:
                exist=records_dict[hash]
            except KeyError:
                records_dict[hash]=new_records
                #corpus_dict[hash]=description
                hashes.append(hash)
            else:
                try:
                    oldtime = records_dict[hash].split('||')[7]
                    olddate = oldtime.split(' ')[0]
                    olddate = int(''.join(olddate.split('-')))
                except Exception as e:
                    print('expection 1',e)
                    print(oldtime)
                    sys.exit()
                try:
                    if date<olddate:
                        records_dict[hash] = new_records
                        print('!!!two same text:',olddate,date)
                        print(olddate,' deleted')
                except Exception as e:
                    print('expection 2',e)
                    print(id)
                    print(date)
                    oldid = records_dict[hash].split('||')[0]
                    print(oldid)
                    print(olddate)
                    sys.exit()
'''
            else:
                same_log.write('!!!!!!2 same text:\n')
                same_log.write(str(hash)+':'+exist+'\n')
                same_log.write(str(hash)+':'+description+'\n')
'''



for h1 in hashes:
       for h2 in hashes:
            if h1 in records_dict and h2 in records_dict:
               if  h1!=h2:
                   sim=h1.similarity(h2)
                   if sim>=sim_threshold:
                       #similar_log.write('!!!!!!2 similar text:\n')
                       #similar_log.write(str(h1)+':' + corpus_dict[h1]+'\n')
                       #similar_log.write(str(h2)+':' + corpus_dict[h2]+'\n')
                       print(h1)
                       time1=records_dict[h1].split('||')[7]
                       date1 = time1.split(' ')[0]
                       date1 = int(''.join(date1.split('-')))
                       time2=records_dict[h2].split('||')[7]
                       date2 = time2.split(' ')[0]
                       date2 = int(''.join(date2.split('-')))
                       #print('!!!!!!2 similar text:',date1,date2)
                       if date1<date2:
                           #corpus_dict.pop(h2, 'not found')
                           records_dict.pop(h2,'not found')
                           print(date2,' deleted')
                       else:
                           #corpus_dict.pop(h1, 'not found')
                           records_dict.pop(h1,'not found')
                           print(date1, ' deleted')

end_time = time.time()


print('before deduplication:%d records' % i)
print('after hashing:%d different records remained' % len(hashes))
print('after deduplication: %d dissimilar records remained'%len(records_dict))
print ('time used %f(hour)' % ((end_time - start_time) / 3600))

for hash in records_dict:
    dedup_records.write(records_dict[hash]+'\001')
    #dedup_corpus.write(corpus_dict[hash])


