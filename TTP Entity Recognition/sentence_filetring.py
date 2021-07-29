# -*- coding=utf-8 -*-
import os
import Levenshtein

path=r"E:\my papers\TAG\experiments"
files=os.listdir(path)

f_wn=open(r"E:\my papers\TAG\experiments\nottp_sentence_5_new.txt",'a',encoding = 'utf-8')
f_wt=open(r"E:\my papers\TAG\experiments\ttp_sentence_5_new.txt",'a',encoding = 'utf-8')

ttp_first=["淘宝","刷单","刷销量","降权","黑搜","刷评论","天猫","内部优惠券","刷好评","空包","淘宝客","淘客","黑钻","互刷","直通车","花呗套现","虚假交易","支付宝","花呗","京东","套现","闲鱼","长尾词","裂变","白号","白条套现","刷手"]

def getMaxCommonSubstr(s1, s2):

    len_s1 = len(s1)
    len_s2 = len(s2)

    record = [[0 for i in range(len_s2 + 1)] for j in range(len_s1 + 1)]

    maxNum = 0
    p = 0

    for i in range(len_s1):
        for j in range(len_s2):
            if s1[i] == s2[j]:
                record[i + 1][j + 1] = record[i][j] + 1

                if record[i + 1][j + 1] > maxNum:
                    maxNum = record[i + 1][j + 1]
                    p = i

    return maxNum, s1[p + 1 - maxNum: p + 1]

def cluster(str1_set,str2_set,tc):
    simi_sen=[]
    for i in range(len(str1_set)):
        for j in range(len(str2_set)):
            if str1_set[i]!=str2_set[j]:
                distance = Levenshtein.ratio(str1_set[i].strip("\n"),str2_set[j].strip("\n"))
                if distance>tc:
                    #print(str1_set[i].strip("\n"),str2_set[j].strip("\n"),distance)
                    simi_sen.append(str2_set[j])
    return simi_sen

def all_sentence():
    all_sentences=[]
    with open("E:\my papers\TAG\experiments\corpus\dedup_records(5).txt", encoding='utf-8') as f:
        lines = f.readlines()
        c = 1
        line = []
        while (c < 1000):
            c1 = c * 7
            ea_line = lines[0].split("||")[c1]
            c = c + 1
            line.append(ea_line)
        for i in line:
            i = i.replace("？", "，")
            i = i.replace("?", "，")
            i = i.replace("！", "，")
            i = i.replace("!", "，")
            i = i.replace("。", "，")
            i = i.replace("\u3000", "")
            sentences = i.split("，")
            for j in sentences:
                all_sentences.append(j)
    return all_sentences

def first_sentence():
    first_sentences=[]
    simi_fs1=[]
    simi_fs2 = []
    with open("E:\my papers\TAG\experiments\corpus\dedup_records(5).txt",encoding='utf-8') as f:
        lines=f.readlines()
        c=1
        line=[]
        while(c<1000):
            c1=c*7
            ea_line=lines[0].split("||")[c1]
            c=c+1
            line.append(ea_line)
        for i in line:
            i=i.replace("？","，")
            i = i.replace("?", "，")
            i = i.replace("！", "，")
            i = i.replace("!", "，")
            i = i.replace("。", "，")
            i=i.replace(" ","")
            first=(i.split("，"))[0]
            first=first.replace("\u3000","")
            first_sentences.append(first)


    for i in range(len(first_sentences)-1):
        j=i+1
        while(j<len(first_sentences)):
            if first_sentences[i]!=first_sentences[j]:
                distance=Levenshtein.ratio(first_sentences[i], first_sentences[j])
               # print(first_sentences[i],first_sentences[j],distance)

                if distance>0.5 and distance<0.8:
                  #  print(first_sentences[i],first_sentences[j],distance)
                    simi_fs1.append(first_sentences[i])
                    simi_fs2.append(first_sentences[j])
              #  print(simi_fs1,simi_fs2)
            j=j+1


    common_str=[]
    for i in range(len(simi_fs1)):
        cn=1
        while(cn>0):
            [lenMatch,strMatch]=getMaxCommonSubstr(simi_fs1[i],simi_fs2[i])
            simi_fs1[i]=simi_fs1[i].replace(strMatch,"")
            simi_fs2[i]=simi_fs2[i].replace(strMatch,"")
            cn=len(strMatch)
            common_str.append(strMatch)

    no_ttp=[]
    retD = list(set(first_sentences).difference(set(simi_fs1)))
    no_ttp=list(set(retD).difference(set(simi_fs2)))
    return(no_ttp,common_str,first_sentences)

def iteration(simi_sen_1,center):
    simi_sen = cluster(simi_sen_1, str2_all, 0.5)
    str_all = list(set(str2_all).difference(set(simi_sen)))
    rate = (len(simi_sen) - len(simi_sen_1)) / len(simi_sen_1)
    return rate,simi_sen,str_all

def remove_ttp_fir(all_sentences):
    all_ttp=[]
    for i in all_sentences:
        for j in ttp_first:
            if j in i:
                all_ttp.append(i)
                break

    all_sentences = list(set(all_sentences).difference(set(all_ttp)))
    return all_sentences


[center,common,first_sentence]=first_sentence()
simi_all=[]
all_sentences=all_sentence()
all_sentences_nofirst = list(set(all_sentences).difference(set(first_sentence)))
all_sentences_nottp=remove_ttp_fir(all_sentences_nofirst)
center=remove_ttp_fir(center)
simi_sen_1=cluster(center,all_sentences_nottp,0.4)
simi_all.append(simi_sen_1)
str2_all=list(set(all_sentences_nottp).difference(set(simi_sen_1)))
rate = (len(simi_sen_1) - len(center)) / len(center)
while (rate>0.1):
    [rate,simi_sen_1,str2_all]=iteration(simi_sen_1,str2_all)
    simi_all.append(simi_sen_1)

nottp_sentence=[]
for i in simi_all:
    for j in i:
        nottp_sentence.append(j)
        f_wn.write(j)
        f_wn.write("\n")

ttp_sentence=[]
ttp_sentence=list(set(all_sentences_nottp).difference(set(nottp_sentence)))
print(len(ttp_sentence))

for i in ttp_sentence:
    f_wt.write(i)
    f_wt.write("\n")




