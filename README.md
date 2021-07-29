# TAG


this project contains three modules:
1. preprocessing
2. topic terms identification
3. TTP entity recognition

all the required data are given in the data directory:
1.part_of_corpus.txt
2.seed blackwords.txt
3.all_dict.txt
...

The usages of each module are shown as below:

1. preprocessing

--preprocess.py
   this flie contains functions for read our corpus, get statistics， remove deduplications and errors
   the corpus file should be separated by lines, each line is in the format of:
   crawler_keywords||data_source||url_of_article||title_of_article||content_of_article||crawling_date
   e.g.,
   群刷||搜狐||http://m.sohu.com/a/204669186_264933||77号调查丨你信赖的网店好评可能全是”刷“出来,而参与刷单的或许...||近日,记者在腾讯QQ群搜索中输入关键词“刷单”,发现没有群符合要求,而当将关键词变成一个“刷”字时,结果让人吃惊,各种“淘宝互刷”群出现,而且清一色都是... ||2017-11-16  

--sentence_parser.py
  this file is used to split each article into sentences，and then cut sentences into words
  e.g., 
  the function cut_sentences (text, punts) split the text into sentences according to chinese punts （，；。？！,;?!）
  the function cut_words(sentence, segmentor,filter=[]) uses a segmentor to cut sentence into words, the list filter can be spcified by user (e.g., filtering stopwords, numbers or urls)
  
  after parsing all the articles, we can save all the cutted sentences in a txt file for the next steps

--scanner.py
  this file is used to identify unknown words that are composed of n-grams （in current implementation， n is set to 3）
  the identified new words can be saved in a new dict along with other dicts (e.g., sogou dict)
  
  after identifying new words, the sentences should be re-segmented by repeating the sentence_parser.py
  
2. topic terms identification

--train_word2vec.py 
  this file is used to train a wordembedding model using Gensim's Word2vec model  (https://radimrehurek.com/gensim/)
  usage:
  #load corpus
  corpus=MyCorpus(dirname=$corpus_path$,filename=$corpus_file$,filter=$words_to_be_filtered$)
  
  #train word2vec rmodel
  word2vec=Word2Vec(corpus,size=200,min_count=1)
  '''
    :param size: the dimension of word embedding vectors
    :param min_count: the least occurrence of a word
    :return: the word2vec model
  '''
  
  #save word2vec model
  word2vec.save('model.word2vec')
  
  
--extract_bw.py
   this file contains similarity metrics for extarcting topic terms that are semantically and structurally similar to seed blackwords
   e.g.,
   word_sim(word1,word2,word2vec) calculates the cosine similarity of two word based on their word embeddings obtained from the word2vec model trained in the above step
   levenshtein_distance calculates the edit distance of two words
   LF2(word,seed_bw,a,b,threshold2,model) decides if the word is similar to one of the seed balckwords by mearsuring the similarity:
   
      a*word_sim(bw, word, model, 'cosine') +b/(levenshtein_distance(bw, word)+1) (a, b and threshold2 can be pre-defined by users)
	  
3. TTP Entity Recognition

-- Sentence_filtering.py
   this file is used to divide sentences into sentences containing TTP terms and sentences not containing TTP terms.
   e.g.,
   getMaxCommonSubstr() finds the common strings for all first sentences. 
   first_sentence() divides first sentences into TTP sentences and sentences not containing TTP (Ds).
   cluster() finds the non-first sentences which are similar to any sentences in Ds.


-- TTP recognition.py
   this file is used to recognize TTP terms from sentences.
   e.g.,
   wp(dep,seg), vob(dep,pos,seg), ATT(dep,pos,seg,sentence), sbv(dep,seg,sentence), length(seg) are five rules to recognize TTP terms.


