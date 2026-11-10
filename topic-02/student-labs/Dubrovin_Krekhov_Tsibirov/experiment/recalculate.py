# coding: utf-8
# Вставьте авторские Title + Abstract + Keywords в reference_A_en.txt (самостоятельно скопировав по DOI).
from pathlib import Path
from collections import Counter
import math, re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
ROOT=Path(__file__).parent
def bleu(ref,cand):
    ref=ref.lower().split(); cand=cand.lower().split()
    if not cand: return 0
    p=[]
    for n in range(1,5):
        r=Counter(tuple(ref[i:i+n]) for i in range(len(ref)-n+1))
        c=Counter(tuple(cand[i:i+n]) for i in range(len(cand)-n+1))
        if not c: return 0
        hits=sum(min(count,r[ng]) for ng,count in c.items())
        if not hits: return 0
        p.append(hits/sum(c.values()))
    bp=min(1,math.exp(1-len(ref)/len(cand)))
    return bp*math.exp(sum(math.log(x)/4 for x in p))
def cosine(ref,cand):
    v=TfidfVectorizer(smooth_idf=True,norm='l2', token_pattern=r'(?u)\b\w+\b')
    x=v.fit_transform([ref.replace(';',''),cand.replace(';','')])
    return float(cosine_similarity(x[0],x[1])[0,0])
reference=(ROOT/'reference_A_en.txt').read_text(encoding='utf-8')
for f in sorted((ROOT/'translations').glob('*.txt')):
    text=f.read_text(encoding='utf-8').split('PART B')[0].replace('PART A','',1).strip()
    print(f.stem, 'BLEU-4',round(bleu(reference,text),4),'cosine TF-IDF',round(cosine(reference,text),4))
