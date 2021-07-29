from gensim.models import Word2Vec
from gensim.models.phrases import Phrases,Phraser
from gensim import corpora
from collections import Counter
import os
import math
import numpy
import jieba
import chardet
import codecs
import re
#import Levenshtein
from pyltp import SentenceSplitter,Segmentor,Postagger
from sklearn.cluster import KMeans

def cut_words_v0(sentence, filter=[]):#replace number,url,cutwords用pos
    '''

    :param sentence:
    :param filter:
    :return:
    '''
    #urls = set()
    #numbers=set()
    words = []
    #number = re.compile('(?:\+|-)?\d+\.?\d*%*')
    url1 = re.compile('https?://[a-zA-Z0-9?/&=:@%-.]+')
    url2 = re.compile('www\.[a-zA-Z0-9?/&=:@%-]+\.[a-zA-Z0-9?/&=:@%-.]+')
    url3=re.compile('[a-zA-Z0-9?/&=:@%-.]+\.(?:com|net|cn|org|html)')
    for str in re.findall(url1, sentence,):
        #urls.add(str)
        sentence = sentence.replace(str, 'url')
    for str in re.findall(url2, sentence,):
        #urls.add(str)
        sentence = sentence.replace(str, 'url')
    for str in re.findall(url3, sentence):
        #urls.add(str)
        sentence = sentence.replace(str, 'url')
    #for str in re.findall(number, sentence):
        #sentence = sentence.replace(str, 'num')
    #temp = jieba.cut(sentence, cut_all=False)
    temp=segmentor.segment(sentence)
    for word in temp:
        if word not in filter:
            if word not in ['\t', '\n', ' ']:
                words.append(word)
            else:
                words.append(' ')
    return words
def cut_words_v1(sentence,trigram,bigram,filter=[]):
    words=cut_words_v0(sentence,filter)
    return  trigram[bigram[words]]

def split(sentence, gram):
    gram=''.join(gram.split('_'))
    for str in re.findall(gram, sentence):
        sentence = sentence.replace(str, ' '+gram+' ')
    parts=sentence.split(' ')
    return parts

def cut_words_v2(sentence, squagrams,trigrams,bigrams,filter=[]):
    words=[]
    for gram in squagrams:
        if gram in sentence:
            sentence = split(sentence, gram)
    for gram in trigrams:
        if gram in sentence:
            sentence = split(sentence, gram)
    for gram in bigrams:
        if gram in sentence:
            sentence = split(sentence, gram)
    for part in sentence:
        if part in squagrams + trigrams + bigrams:
            words.append(part)
        else:
            part_words = cut_words_v0(part,filter)  # pyltp分词
        words.extend(part_words)
    return words

class MyCorpus(object):
    def __init__(self,dirname=None,filename=None,outer=[],use_outer=False,filter=[]):
        self.dirname=dirname
        self.filename=filename
        self.outer=outer
        self.use_outer=use_outer
        self.filter=filter
        self.vocab=set()
    def __iter__(self):
        if self.dirname!=None and self.filename==None:
            for filename in os.listdir(self.dirname):
                if filename not in self.outer:
                    text = open(os.path.join(self.dirname, filename), 'r',encoding='utf-8').read()
                    urls,numbers,words=cut_words_v0(text,filter)
                    self.vocab=self.vocab|set(words)
                    #print(words)
                    #print(filename)
                    yield words
                else:
                    if self.use_outer==True:
                        with open(os.path.join(self.dirname, filename),'r', encoding='utf-8') as fd:
                            for line in fd:
                                urls, numbers, words=cut_words_v0(line,filter)
                                self.vocab=self.vocab|set(words)
                                yield words
        if self.dirname!=None and self.filename!=None:
            records=open(os.path.join(self.dirname,self.filename),'r',encoding='utf-8').read().split('\001')
            for i in range(len(records)-1):
                article=records[i].split('||')[2]
                #print(article)
                print('%d articles loaded' % (i + 1))
                words=cut_words_v0(article,self.filter)
                postags=  postagger.postag(words)
                if len(words)==len(postags) :
                    clean_words=[]
                    for i in range(len(words)):
                        if postags[i] not in ['wp','nt']:
                            clean_words.append(words[i])
                self.vocab=self.vocab|set(clean_words)
                if i==len(records)-2:
                    print('%d articles loaded'%(i+1))
                    print('%d vocab'%len(self.vocab))
                yield clean_words
        if self.dirname==None and self.filename==None:
            for outfile in self.outer:
                with open(outfile, 'r', encoding='utf-8') as fd:
                    for line in fd:
                        urls, numbers, words = cut_words_v0(line, filter)
                        self.vocab = self.vocab|set(words)
                        yield set(words)

def predict_prob(iword,oword,model):
    if iword in model.wv.vocab and  oword in model.wv.vocab:
        iword_vec = model[iword]
        oword = model.wv.vocab[oword]
        oword_l = model.syn1[oword.point].T
        dot = numpy.dot(iword_vec, oword_l)
        lprob = -sum(numpy.logaddexp(0, -dot) + oword.code*dot)
        prob=math.exp(lprob)
        return prob
    else:
        return -1
def extract_by_word2vec(model,doc,topK):
    words = [w for w in doc if w in model]
    sum_prob = {w:sum([predict_prob(w,u,model) for u in words]) for w in words}
    temp=Counter(sum_prob).most_common(topK)
    keywords=[w[0] for w in temp]
    return keywords

def save2file(word2vec,file_path):
    num=len(word2vec.wv.vocab)
    dim=word2vec.vector_size
    word_embeddings=open(file_path,'w',encoding='utf-8')
    word_embeddings.write(str(num)+' '+str(dim))
    word_embeddings.write( '\n ')
    for word in word2vec.wv.vocab:
        word_vec = word2vec[word]
        word_embeddings.write(word+' ')
        for f in word_vec:
            word_embeddings.write(str(f) + ' ')
        word_embeddings.write( '\n ')
    print('word2vec:%d vocab,embedding dim:%d'%(num,dim))


filter=set( [line.strip() for line in open('../../dicts/symbols.txt',encoding='utf-8').readlines()])|set( [line.strip() for line in open('../../dicts/stopwords.txt',encoding='utf-8').readlines()])
segmentor = Segmentor()
segmentor.load_with_lexicon('E:\data\ltp-data\ltp-data-v3.3.1\cws.model','../../dicts/all.dict')
postagger = Postagger()
postagger.load('E:\data\ltp-data\ltp-data-v3.3.1\pos.model')

corpus=MyCorpus(dirname='../../corpus',filename='dedup_records(5-13).txt',filter=filter)

'''
bigram=Phrases(corpus,2,min_count=5,threshold=20, max_vocab_size=40000000, delimiter='_', progress_per=1000)
bigram.save('models/phrases(5-9).bigram')
bigram_file=open('results/bigrams(5-9).txt','w',encoding='utf-8')
bigrams={}
for gram, score in bigram.export_phrases(corpus,out_delimiter='_', as_tuples=False):
    a=gram.split('_')[0]
    b = gram.split('_')[1]
    if a!=' 'and b!=' ':
        try:
            bigrams[gram]=score
        except KeyError:
            pass
#num_bigram2=len(bigrams)
bigrams=Counter(bigrams).most_common()
for gram in bigrams:
  bigram_file.write(gram[0]+':'+str(gram[1]))
  bigram_file.write('\n')

#bigramer=Phraser(bigram)
trigram = Phrases(bigram[corpus],3,min_count=4,threshold=15, max_vocab_size=40000000, delimiter='_', progress_per=1000)#trigram控制长度
trigram.save('models/phrases(5-9).trigram')
trigram_file=open('results/trigrams(5-9).txt','w',encoding='utf-8')
trigrams={}
for gram, score in trigram.export_phrases(bigram[corpus],out_delimiter='_', as_tuples=False):
    words=gram.split('_')
    for word in words:
        if word==' ':
            continue
        try:
            trigrams[gram]=score
        except KeyError:
            pass
#num_trigram2=len(trigrams)
trigrams=Counter(trigrams).most_common()
for gram in trigrams:
  trigram_file.write(gram[0]+':'+str(gram[1]))
  trigram_file.write('\n')

#trigramer=Phraser(trigram)
squagram = Phrases(trigram[corpus],4,min_count=3,threshold=10, max_vocab_size=40000000, delimiter='_', progress_per=1000)#trigram控制长度
squagram.save('models/phrases(5-9).squagram')
squagram_file=open('results/squagrams(5-9).txt','w',encoding='utf-8')
squagrams={}
for gram, score in squagram.export_phrases(squagram[corpus],out_delimiter='_', as_tuples=False):
    words=gram.split('_')
    for word in words:
        if word==' ':
            continue
        try:
            squagrams[gram]=score
        except KeyError:
            pass
squagrams=Counter(squagrams).most_common()
for gram in squagrams:
  squagram_file.write(gram[0]+':'+str(gram[1]))
  squagram_file.write('\n')
'''
'''
bigram=Phrases.load('models/phrases(5-9).bigram')
trigram=Phrases.load('models/phrases(5-9).trigram')
squagram=Phrases.load('models/phrases(5-9).squagram')
'''
word2vec=Word2Vec(corpus,size=200,min_count=1,window=11,workers=3,sg=1,hs=1)#skip-gram haffman tree#trigram[bigram[corpus]]
word2vec.save('../../models/words(5-13)_v3.word2vec')
#save2file(word2vec,'results/phrase_embedding_stopwords(5-9)_v1.txt')
#print('黑搜,黑搜索:',word2vec.wv.similarity("黑搜",'黑搜索'))
#print('淘客,淘宝客:',word2vec.wv.similarity("淘客",'淘宝客'))
#print('单号网,空包网:',word2vec.wv.similarity("单号网",'空包网'))
#print('刷好评,刷评论:',word2vec.wv.similarity("刷好评",'刷评论'))


'''
word2vec=Word2Vec(corpus,size=200,min_count=1,window=11,workers=3,sg=1,hs=1)#skip-gram haffman tree
word2vec.save('models/words_stopwords(5-9).word2vec')
save2file(word2vec,'results/word_embedding_stopwords(5-9).txt')

'''
