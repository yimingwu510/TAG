from ltp import LTP
from collections import Counter
import re

f_ttp=open(r"E:\my papers\TAG\experiments\ttp_5_new.txt",'a',encoding = 'utf-8')
fa=open("E:\my papers\TAG\experiments\corpus\dedup_records(5).txt",'r',encoding='utf-8')
corpus=fa.read()


def wp(dep,seg):
    c = 0
    wp=[]
    wp_result=[]
    for i in dep[0]:
        if i[2]=='WP':
            c=c+1
            wp.append(i[1])

    b = dict(Counter(wp))
    wp_center=[key for key,value in b.items()if value > 1]

    arra=[]
    for i in wp_center:
        c_list = []
        for j in dep[0]:
            if j[1]==i and j[2]=="WP":
                c1=j[0]
                c_list.append(c1)
        arra.append(c_list)

    for i in arra:
        head=i[0]
        wei=i[1]
        c=head+1
        str1=[]
        while(c<wei):
            str1.append(seg[0][c-1])
            c = c + 1
        s = "".join(str1)
        wp_result.append(s)
    return wp_result

def vob(dep,pos,seg):
    arra=[]
    for i in range(len(dep[0])):
        c1 = dep[0][i][0]
        c2 = dep[0][i][1]
        if dep[0][i][2] == 'VOB' and pos[0][c2-1]=='n':
            print("333",seg[0][c2-1])
            arra.append(seg[0][c2-1])
    return arra

def ATT(dep,pos,seg,sentence):
    att=[]
    att_result=[]
    for i in range(len(dep[0])):
        c1 = dep[0][i][0]
        c2 = dep[0][i][1]
        if dep[0][i][2] == 'ATT' and pos[0][c2-1]== 'n':
            att.append(seg[0][c1-1])
            att.append(seg[0][c2-1])
    s = "".join(att)
   # print(s)
    if len(s)>0 and s in sentence:
      #  print("444",s)
        att_result.append(s)
    return att_result

def sbv(dep,seg,sentence):
    arra=[]
    for i in range(len(dep[0])):
        sbv = []
        c1 = dep[0][i][0]
        c2 = dep[0][i][1]
        if dep[0][i][2] == 'SBV':
            sbv.append(seg[0][c1-1])
            sbv.append(seg[0][c2-1])
        s = "".join(sbv)
        if s in sentence and len(s)>0:
            #print("555",s)
            arra.append(s)
    return arra

def length(seg):
    arra=[]
    for i in seg[0]:
        if len(i)>3:
           # print("666",i)
            arra.append(i)
    return arra

def filter(arra):
    result=[]
    for i in arra:
        try:
            list_index = [j.start() for j in re.finditer(i, corpus)]
            for k in list_index:
                c1 = int(k) - 100
                c2 = int(k) + 100
                if c1 < 0:
                    c1 == 0
                window = corpus[c1:c2]
                for n in topicterm:
                    if n in window:
                        print("+++",i)
                        result.append(i)
                        break
                else:
                    continue
            break
        except:
            continue

    return result

topicterm=["刷单","刷销量","降权","黑搜","刷评论"]
with open(r"E:\my papers\TAG\experiments\ttp_sentence_5_new.txt",'r',encoding = 'utf-8') as f:
    lines=f.readlines()
    for sentence in range(1,6000):
        ltp = LTP()  # 默认加载 Small 模型
        seg, hidden = ltp.seg([lines[sentence]])
        pos = ltp.pos(hidden)
        ner = ltp.ner(hidden)
        srl = ltp.srl(hidden)
        dep = ltp.dep(hidden)
        sdp = ltp.sdp(hidden)
        wp_result=wp(dep,seg)
        vob_result=vob(dep,pos,seg)
        ATT_result=ATT(dep,pos,seg,lines[sentence])
        sbv_result=sbv(dep, seg, lines[sentence])
        length_result=length(seg)
      #  qq_result=qq(lines[sentence])
        wp_ttp = []
        wp_ttp = filter(ATT_result)
        vob_ttp=[]
        vob_ttp=filter(vob_result)
        ATT_ttp=[]
        ATT_ttp = filter(ATT_result)
        sbv_ttp = []
        sbv_ttp = filter(sbv_result)
        length_ttp = []
        length_ttp = filter(length_result)
      #  qq_ttp = []
       # qq_ttp = filter(qq_result)
        '''
        for i in vob_result:
            count=corpus.count(i)
          #  print("vvv",i)
            if count>2:
                f_ttp.write(i)
                f_ttp.write("||")
                f_ttp.write(str(count))
                f_ttp.write("\n")
        for i in ATT_result:
            count=corpus.count(i)
         #   print("aaa",i)
            if count>2:
                f_ttp.write(i)
                f_ttp.write("||")
                f_ttp.write(str(count))
                f_ttp.write("\n")
        for i in sbv_result:
            count=corpus.count(i)
            if count>2:
                f_ttp.write(i)
                f_ttp.write("||")
                f_ttp.write(str(count))
                f_ttp.write("\n")
            #print(i, count)
         #   print("sss",i)
          #  if count>2:
           #     print("&&&",i)
        for i in length_result:
            count=corpus.count(i)
            if  count>2:
                f_ttp.write(i)
                f_ttp.write("||")
                f_ttp.write(str(count))
                f_ttp.write("\n")
            #print(i, count)
         #   print("lll",i)
         #   if count>2:
          #      print("&&&",i)
          '''
