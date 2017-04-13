# coding: utf-8

import collections
import itertools
import os
import pickle
import shutil
import sys

# # Creating `.dict` files

def create_vocab_for_corpus(fn,dev_size=0.1):
    """Create the vocabulary and word embeddings for a single corpus."""
    
    # compute the size of the train/dev set
    num_sentences = sum(1 for line in open(fn, 'r'))
    num_dev_sentences = int(num_sentences*dev_size)
    num_training_sentences = num_sentences - num_dev_sentences
    
    # count tokens in the train set
    count = collections.Counter()
    with open(fn, 'r') as text:
        for line in itertools.islice(text,num_training_sentences):
            for tok in line.split():
                count[tok.encode('utf8')] += 1
    
    vocab_by_freq = [tok for tok,num in count.most_common()]
    vocab = dict(count)
    w2i = {b'_PAD': 0, b'_GO': 1, b'_EOS': 2, b'_UNK': 3}
    w2i.update(zip(vocab_by_freq, range(4,len(vocab_by_freq)+4)))
    i2w = {v: k for k,v in w2i.items()}
    return (vocab, w2i, i2w)


def create_vocab_for_parallel_corpus(text_en,text_fr):
    """Create the vocabulary and word embeddings for a parallel corpus."""
    vocab_en, w2i_en, i2w_en = create_vocab_for_corpus(text_en)
    vocab_fr, w2i_fr, i2w_fr = create_vocab_for_corpus(text_fr)
    print("vocab size: en={0:d}, fr={1:d}".format(len(vocab_en),len(vocab_fr)))
    vocab = {'en': vocab_en, 'fr': vocab_fr}
    w2i   = {'en': w2i_en  , 'fr': w2i_fr  }
    i2w   = {'en': i2w_en  , 'fr': i2w_fr  }
    return (vocab, w2i, i2w)


def create_and_dump_vocab(data_dir,
                          text_en='text.en',
                          text_fr='text.fr',
                          vocab_dict='vocab.dict',
                          w2i_dict='w2i.dict',
                          i2w_dict='i2w.dict'):
    data_files = [text_en,text_fr,vocab_dict,w2i_dict,i2w_dict]
    data_files = list(map(lambda fn: os.path.join(data_dir,fn),data_files))
    text_en, text_fr, vocab_dict, w2i_dict, i2w_dict = data_files

    vocab, w2i, i2w = create_vocab_for_parallel_corpus(text_en,text_fr)
    pickle.dump(vocab, open(vocab_dict,'wb'))
    pickle.dump(w2i, open(w2i_dict,'wb'))
    pickle.dump(i2w, open(i2w_dict,'wb'))

if __name__ == "__main__":
    if os.path.isdir(sys.argv[1]):
        create_and_dump_vocab(sys.argv[1])
