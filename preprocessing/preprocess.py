import os
import shutil
import random
import codecs
import chardet
import heapq
from xlwt import *
from xlrd import *
import numpy
#from xlutils.copy import copy


def merge_file(dirname,newfile,filter):
    for filename in os.listdir(dirname):
        if filename not in filter:
            print(filename)
            with codecs.open(os.path.join(dirname,filename), 'rb') as f:
                    data = f.read()
                    encodeInfo = chardet.detect(data)
                    #text= models.decode(encodeInfo['encoding'])
            for line in open(os.path.join(dirname,filename), 'r',encoding=encodeInfo['encoding']).readlines():
                    newfile.write(line)
            newfile.write('\n')

def save_words(words,infile):
    file=open(infile,'w',encoding='utf-8')
    for word in words:
            file.write(word+'\n')

def sample_articles(all_articles,sampled_articles,sample_rate):
    articles=open(all_articles,encoding='utf-8').read().split('\001')
    total_num=len(articles)-1
    sampled_num=int(total_num*sample_rate)
    samples=random.sample([i for i in range(total_num)],sampled_num)
    with open(sampled_articles,'w',encoding='utf-8') as outfile:
        for i in samples:
            outfile.write(articles[i]+'\001')
    print('%d articles in total ,%d sampled'%(total_num,sampled_num))

def sample_sentences_by_articles(all_sentences,sampled_sentences,sample_rate):
    articles=open(all_sentences,encoding='utf-8').read().split('\n\n')
    total_num=len(articles)
    sampled_num=int(total_num*sample_rate)
    samples=random.sample([i for i in range(total_num)],sampled_num)
    with open(sampled_sentences,'w',encoding='utf-8') as outfile:
        for i in samples:
            outfile.write(articles[i]+'\n\n')
    print('%d articles in total,%d  sampled'%(total_num,sampled_num))

def sample_sentences(all_sentences,sampled_sentences,sample_rate):
    sentences=list(set(open(all_sentences,encoding='utf-8').read().split('\n')))
    total_num=len(sentences)-1
    sampled_num=int(total_num*sample_rate)
    samples=random.sample([i for i in range(total_num) if sentences[i]!=''],sampled_num)
    with open(sampled_sentences,'w',encoding='utf-8') as outfile:
        for i in samples:
            outfile.write(sentences[i]+'\n')
    print('%d sentences,%d sampled'%(total_num,sampled_num))

def dedup_sth(filename=None):
    if filename!=None:
        sth=set([line.rstrip() for line in open(filename,encoding='utf-8').readlines()])
    with open(filename,'w',encoding='utf-8')as outfile:
        for each in sth:
            outfile.write(each+'\n')
    print('%d object saved in %s'%(len(sth),filename))

#rewrite grams without '_' and remove same words after rewiriting
def merge_sth(oldfile,newfile):
    print('merge file')
    if oldfile!=None:
        sth = set([line.rstrip() for line in open(oldfile, encoding='utf-8').readlines() if not line.startswith('#')])
    oldnum=len(sth)
    newnum=0
    with open(newfile, 'w', encoding='utf-8')as outfile:
        for one in sth:
            if '_' in one:
                one='\t'.join(one.split('_'))
            if '\t' in one:
                oldone=one
                one = ''.join(one.split('\t'))
                merge = 0
                for another in sth:
                    oldanother=another
                    another = ''.join(another.split('\t'))
                    if one==another and oldone!=oldanother:
                        merge=1
                        break
                    if one in another and one!=another:
                        merge = 1
                        break
                if merge == 0:
                    outfile.write(oldone + '\n')
                    newnum+=1
            else:
                    outfile.write(one + '\n')
                    newnum += 1
    print(oldnum,newnum)
    dedup_sth(newfile)

def rewrite_sth(oldfile,newfile):
    if oldfile!=None:
        sth = set([line.rstrip() for line in open(oldfile, encoding='utf-8').readlines() if not line.startswith('#')])
        print('%d items in %s'%(len(sth),oldfile))

    with open(newfile, 'w', encoding='utf-8')as outfile:
        for one in sth:
            one=''.join(one.split('\t'))
            outfile.write(one+'\n')
    #dedup_sth(newfile)

def get_update_whitewords(pred_blackwords,checked_blackwords):
    pred_bw = set(open(pred_blackwords, encoding='utf-8').read().split())
    blackwords = set(open(checked_blackwords, encoding='utf-8').read().split())
    whitewords = pred_bw - blackwords
    print('%d white words updated'%len(whitewords))
    shutil.copyfile('results/white_words.txt', 'results/white_words_copy.txt')
    white = open('results/white_words.txt', 'a', encoding='utf-8')
    for word in whitewords:
        white.write(word + '\n')
    dedup_sth('results/white_words.txt')

def get_update_blackwords(old_blackwords, new_blackwords):
    new_bw = set(line.strip() for line in open(new_blackwords, encoding='utf-8').readlines())
    print('%d blackwords updated'%len(new_bw))
    old_file = open(old_blackwords, 'a', encoding='utf-8')
    for word in new_bw:
       old_file.write(word + '\n')
    dedup_sth(old_blackwords)

def filter_sth(source_file,filter_file,target_file=None):
    source=set([line.rstrip() for line in open(source_file,encoding='utf-8').readlines() if not line.startswith('#')])
    filter=set([line.rstrip() for line in open(filter_file,encoding='utf-8').readlines() if not line.startswith('#')])
    sth=source-filter
    if target_file:
        file=target_file
    else:
        file= source_file
    with open(file,'w',encoding='utf-8') as newfile:
        for one in sth:
              newfile.write(one+'\n')
        print('%d items saved in %s'%(len(sth),file))

def clean_corpus(records_file,new_records_file):
    records=open(records_file,encoding='utf-8').read().split('\001')
    new_records=open(new_records_file,'w',encoding='utf-8')
    num=0
    for record in records:
        tuple=record.split('||')
        if len(tuple)==8:
            id=tuple[0]
            referer_url=tuple[1]
            description=tuple[2]
            crawler_keyword=tuple[3]
            source=tuple[4]
            groupid=tuple[5]
            abstract=tuple[6]
            pub_time_a = tuple[7]
            if crawler_keyword.startswith('|'):
                crawler_keyword=crawler_keyword[1:]
            if pub_time_a.startswith('|'):
                pub_time_a = pub_time_a[1:]
            #date = pub_time_a.split(' ')[0]
            #month = date.split('-')[1]
            #if month==
            num+=1

            new_record=id+'||'+referer_url+'||'+description+'||'+crawler_keyword+'||'+source+'||'+groupid+'||'+abstract+'||'+pub_time_a
            new_records.write(new_record+'\001')
    print('%d  records'%num)


def summarize_corpus(records_file,corpus_file,source_file,keyword_file):
    records=open(records_file,encoding='utf-8').read().split('\001')
    corpus=open(corpus_file,'w',encoding='utf-8')
    date1=20171231
    date2=20170101
    id1='9999999999'
    id2='0'
    crawler_keywords=set()
    sources={}
    groups=set()
    for record in records:
        tuple=record.split('||')
        if len(tuple)==8:
            id=tuple[0]
            referer_url=tuple[1]
            description=tuple[2]
            corpus.write(description + '\001')
            crawler_keyword=tuple[3]
            if crawler_keyword.startswith('|'):
                crawler_keyword=crawler_keyword[1:]
            source=tuple[4]
            groupid=tuple[5]
            pub_time_a = tuple[7]
            if pub_time_a.startswith('|'):
                pub_time_a = pub_time_a[1:]
            date = pub_time_a.split(' ')[0]
            date=int(''.join(date.split('-')))
            if date<date1:
                date1=date
            if date>date2:
                date2=date
            if id<id1:
                id1=id
            if id>id2:
                id2=id
            crawler_keywords.add(crawler_keyword)
            groups.add(int(groupid))
            try:
                ex=sources[source]
            except KeyError:
                sources[source]=set()

            sources[source].add(referer_url)

    with open(source_file,'w',encoding='utf-8') as outfile:
        for source in sources:
            outfile.write(source+'\n')
            outfile.write('\n'.join(sources[source]))
            outfile.write('\n')
            outfile.write('\r')
    with open(keyword_file,'w',encoding='utf-8') as outfile:
        for keyword in crawler_keywords:
            outfile.write(keyword+'\n')
    print('%d articles'%(len(records)-1))
    print('%d groups,group ids from %s to %s'%(len(groups),heapq.nsmallest(1,groups)[0],heapq.nlargest(1,groups)[0]))
    print('article id from %s to %s'%(id1,id2))
    print('publicating date from %s to %s'%(date1,date2))
    print('%d sources:%s'%(len(sources),','.join(sources)))
    print('%d crawler keywords:%s'%(len(crawler_keywords),','.join(crawler_keywords)))
    print('sources saved in %s, crawler keywords saved in %s'%(source_file,keyword_file))


def get_corpus_by_month(all_records='../corpus/dedup_records(5-9).txt',months=['05','06','07','08','09','10','11','12','01']):
    records = open(all_records, encoding='utf-8').read().split('\001')
    for month in months:
        num=0
        keywords=set()
        month_file='../corpus/corpus_'+month+'.txt'
        month_corpus=open(month_file,'w',encoding='utf-8')
        for record in records:
            tuple = record.split('||')
            if len(tuple) == 8:
                id = tuple[0]
                referer_url = tuple[1]
                description = tuple[2]
                crawler_keyword = tuple[3]
                source = tuple[4]
                groupid = tuple[5]
                abstract = tuple[6]
                pub_time_a = tuple[7]
                if pub_time_a.startswith('|'):
                    pub_time_a = pub_time_a[1:]
                date = pub_time_a.split(' ')[0]
                current_month = date.split('-')[1]
                if current_month not in months:
                    print(date)
                if current_month ==month :#or current_month ==month.lstrip('0'):
                    num+= 1
                    keywords.add(crawler_keyword)
                    month_corpus.write(description + '\001')
                    #new_records=id + '||' + referer_url + '||' + description + '||' + crawler_keyword + '||' + source + '||' + groupid + '||' + abstract + '||' + pub_time_a
                    #month_corpus.write(new_records + '\001')
        print('%d articles in %s-th month,%d crawler keywords'%(num,month,len(keywords)))

def get_corpus_by_source(all_records='../corpus/dedup_records(5-9).txt',sources=['Weibo','News','LunTan','Other','Video','TieBa','Government','WeiXin']):
    records = open(all_records, encoding='utf-8').read().split('\001')
    for source in sources:
        num=0
        keywords=set()
        source_file='../corpus/corpus_'+source+'.txt'
        source_corpus=open(source_file,'w',encoding='utf-8')
        for record in records:
            tuple = record.split('||')
            if len(tuple) == 8:
                description = tuple[2]
                crawler_keyword = tuple[3]
                current_source=tuple[4]
                if current_source not in sources:
                    print(current_source)
                if current_source ==source:
                    num+= 1
                    keywords.add(crawler_keyword)
                    source_corpus.write(description + '\001')
                    #dedup_records_1.write(record + '\001')
        print('%d articles from %s,%d crawler keywords'%(num,source,len(keywords)))

def process_sougoudict(dict_dir):
    dicts=os.listdir(dict_dir)
    for dict in dicts:
        if '.sougou' in dict:
            text = open(os.path.join(dict_dir,dict), encoding='utf-8').read()
            words = set([line.split()[1] for line in text.split('\n') if len(line) > 1])
            newdict = dict.replace('sougou', 'dict')
            new=open(os.path.join(dict_dir,newdict),'w', encoding='utf-8')
            for word in words:
                new.write(word + '\n')

def merge_dict(dicts,filter=set(),newdict=None):
    if len(dicts)==1:
        text = open(dicts[0], encoding='utf-8').read()
        words = set(text.split())-filter
        newdict=dicts[0]
        new=open(newdict, 'w',encoding='utf-8')
        for word in words:
            new.write(word + '\n')
    else:
        new = open(newdict, 'a', encoding='utf-8')
        for dict in dicts:
            text = open(dict, encoding='utf-8').read()
            words = set(text.split())
            for word in words:
                if word not in filter:
                    new.write(word + '\n')
    dedup_sth(newdict)



if __name__==’__main__’:
    #clean_corpus(‘../data/records(10-13).txt’,’../data/records(10-13)_new.txt')
    #summarize_corpus(‘../data/dedup_records(5-13).txt’,’../data/dedup_corpus(5-13).txt','../results/sources(5-13).txt’,’../data/seed_blackwords.txt')
    #get_corpus_by_month(all_records=‘../data/dedup_records(5-13).txt',months=['05','06','07','08','09','10','11','12','01'])
    #get_corpus_by_source(‘../data/dedup_records(5-13).txt')

