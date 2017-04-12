
# coding: utf-8

# In[94]:

import collections
import itertools
from tqdm import tqdm as progress


# # Representing the lexicon as n-ary trees of tokens

# In[95]:

def alphabet_from_text(text):
    alphabet = set()
    for line in text:
        alphabet.update(line)
    return alphabet


# In[96]:

def lexicon_from_alphabet(alphabet):
    return {k:[True,dict()] for k in alphabet}


# In[97]:

def lexicon_from_word(word):
    lex = dict()
    if word:
        prv,nxt = None,lex
        for char in word:
            prv,nxt = nxt,dict()
            prv[char] = [False,nxt]
        prv[char][0] = True
    return lex


# In[98]:

def mergeEntry(ent1,ent2):
    ent1[0] = ent1[0] or ent2[0]
    merge(ent1[1],ent2[1])

def merge(lex1,lex2):
    for k,v in lex2.items():
        if k in lex1:
            mergeEntry(lex1[k],v)
        else:
            lex1[k] = v


# In[99]:

def insert(lex,word):
    i,cur = 0,lex
    for i in range(len(word) - 1):
        if not word[i] in cur:
            break
        cur = cur[word[i]][1]
        i += 1
    if word[i] in cur:
        assert i == len(word) - 1
        cur[word[i]][0] = True
    else:
        merge(cur,lexicon_from_word(word[i:]))


# In[100]:

def tokenise(lex,text):
    cur,toks = lex,[]
    i = 0 # end of previous token
    j = 0 # last valid end state
    k = 0 # current position
    while k < len(text):
        if text[k] in cur:
            end,cur = cur[text[k]]
            k += 1
            if end:
                j = k
        else:
            toks.append(text[i:j])
            i = j
            k = j
            cur = lex
    toks.append(text[i:j])
    return toks


# In[101]:

test_lex_actual = lexicon_from_word('hello')
insert(test_lex_actual,'help')
insert(test_lex_actual,'hell')
test_lex_expected =   {'h': [False, {'e': [False, {'l': [False, {'l': [True, {'o': [True, {}]}], 'p': [True, {}]}]}]}]}
assert test_lex_actual == test_lex_expected

toks_actual = tokenise(test_lex_expected,'helphellohelphell')
toks_expected = ['help','hello','help','hell']
assert toks_actual == toks_expected


# # The MCB tokenisation algorithm

# In[102]:

def mcb_iter(lex,text_in,n=1,initial=0,total=None):
    count = collections.Counter()
    text_out = []
    for i in progress(range(n),initial=initial,total=total):
        for line in text_in:
            toks = tokenise(lex,line)
            for bigram in zip(toks,toks[1:]):
                count[bigram] += 1
            if i == n - 1:
                text_out.append(toks)
        bigram = ''.join(count.most_common()[0][0])
        insert(lex,bigram)
    return text_out


# In[103]:

def mcb(data_file_in,data_patn_out,ns):
    with open(data_file_in, 'r') as text_in:
        text_in = [line.strip() for line in text_in]
        
    abc = alphabet_from_text(text_in)
    lex = lexicon_from_alphabet(abc)
    
    initial,total = 0,ns[-1]
    deltas = map(lambda x: x[1] - x[0],zip([0]+ns,ns))
    for n,delta in zip(ns,deltas):
        text_out = mcb_iter(lex,text_in,delta,initial=initial,total=total)
        with open(data_patn_out.format(n), 'w') as data_file_out:
            for toks in text_out:
                data_file_out.write(' '.join(toks) + '\n')
        initial += delta

# In[104]:

def mcb_continue(data_file_in,data_patn_out,ns):
    with open(data_file_in, 'r') as text_in:
        text_in = [line.strip() for line in text_in]
    
    toks = set(itertools.chain(*[line.split() for line in text_in]))
    lex = lexicon_from_word(toks.pop())
    for tok in toks:
        insert(lex,tok)

    text_in = [line.replace(' '*1,' '*0) for line in text_in]
    
    initial,total = 0,ns[-1] - ns[0]
    deltas = map(lambda x: x[1] - x[0],zip(ns,ns[1:]))
    for n,delta in zip(ns[1:],deltas):
        text_out = mcb_iter(lex,text_in,delta,initial=initial,total=total)
        with open(data_patn_out.format(n), 'w') as data_file_out:
            for toks in text_out:
                data_file_out.write(' '.join(toks) + '\n')
        initial += delta
   

#ns = [100,300,500,1000,3000,5000,10000]
#mcb('goldwater/data/text.fr.raw','in_en_data_mcb_50000/text.fr.{}',ns=ns)

ns = [300,500,1000,3000,5000,10000]
mcb_continue('in_en_data_mcb_50000/text.fr.300','in_en_data_mcb_50000/text.fr.{}',ns=ns)


