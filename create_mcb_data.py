# coding: utf-8

import collections
import itertools
import os
import pickle
import shutil
import tqdm

# # Most Common Bigram Tokenisation

def create_toks_dict(toks_list):
    toks_list = sorted(toks_list)
    return {k:list(sorted(v,key=len,reverse=True))
            for k,v in itertools.groupby(toks_list, key=lambda ln: ln[0])
            if k and k.strip()}

def toks_tokenise_line(line,toks_dict,start=0):
    toks = []
    while start < len(line) - 1:
        if line[start] and line[start].strip():
            for tok in toks_dict[line[start]]:
                if line.startswith(tok,start):
                    start += len(tok)
                    toks.append(tok)
                    break
        else:
            toks.append(' ')
            start += 1
    return toks

def toks_tokenise_text(text,toks_dict):
    count = collections.Counter()
    for line in text:
        toks = toks_tokenise_line(line.strip(),toks_dict)
        for bigram in zip(toks,toks[1:]):
            count[bigram] += 1
    return count

def create_toks_list(text,max_size):
    toks_list = set(itertools.chain(*[line.replace(' '*0,' '*1).strip().split() for line in text]))
    toks_dict = create_toks_dict(toks_list)
    start_size = len(toks_list)
    for _ in tqdm.tqdm(range(start_size,max_size)):
        count = toks_tokenise_text(text,toks_dict)
        most_common = next(x + y \
            for (x, y), count in count.most_common()
            if x and x.strip() and y and y.strip())
        toks_dict[most_common[0]].append(most_common)
        toks_dict[most_common[0]].sort(key=len,reverse=True)
    return tuple(itertools.chain(*toks_dict.values()))

def mcb_tokenise_file(data_file_in,data_file_out,fmax_size,data_file_orig=None):
    with open(data_file_in, 'r') as text_in:
        text_in = text_in.readlines()

    # compute the max size based on the start corpus size
    if data_file_orig:
        with open(data_file_orig, 'r') as text_orig:
            text_orig = text_orig.readlines()
    else:
        text_orig = text_in
    max_size = fmax_size(len(set(itertools.chain(*[line.strip().split() for line in text_orig]))))

    toks_list = create_toks_list(text_in,max_size)
    toks_dict = create_toks_dict(toks_list)
    with open(data_file_out, 'w') as text_out:
        for line in text_in:
            text_out.write(' '.join(toks_tokenise_line(line,toks_dict))+'\n')

def mcb_tokenise_dir(data_dir_in,data_dir_out,fmax_size,
                      text_en='text.en',text_fr='text.fr',
                      mcb_tokenise_en=True,mcb_tokenise_fr=True,data_dir_orig=None):

    # compute paths to input files
    data_files_in = [text_en,text_fr]
    data_files_in = list(map(lambda fn: os.path.join(data_dir_in,fn), data_files_in))
    text_en_in, text_fr_in = data_files_in

    # compute paths to output files
    data_files_out = [text_en, text_fr]
    data_files_out = list(map(lambda fn: os.path.join(data_dir_out,fn), data_files_out))
    text_en_out, text_fr_out = data_files_out

    # compute paths to original files
    if data_dir_orig:
        data_files_orig = [text_en,text_fr]
        data_files_orig = list(map(lambda fn: os.path.join(data_dir_orig,fn), data_files_orig))
        text_en_orig, text_fr_orig = data_files_orig
    else:
        text_en_orig, text_fr_orig = None, None

    # create the output directory
    if not os.path.isdir(data_dir_out):
        os.makedirs(data_dir_out)

    # tokenise by character
    if mcb_tokenise_en:
        mcb_tokenise_file(text_en_in,text_en_out,fmax_size,text_en_orig)
    else:
        shutil.copyfile(text_en_in,text_en_out)
    if mcb_tokenise_fr:
        mcb_tokenise_file(text_fr_in,text_fr_out,fmax_size,text_fr_orig)
    else:
        shutil.copyfile(text_fr_in,text_fr_out)


# # Creating datasets

mcb_tokenise_dir(data_dir_in='in_en_data_50000',
                 data_dir_out='in_en_data_mcb128_50000',
                 mcb_tokenise_en=False,
                 fmax_size=lambda orig_size: orig_size // 128)
mcb_tokenise_dir(data_dir_in='in_en_data_mcb128_50000',
                 data_dir_out='in_en_data_mcb64_50000',
                 mcb_tokenise_en=False,
                 fmax_size=lambda orig_size: orig_size // 64,
                 data_dir_orig='in_en_data_50000')
mcb_tokenise_dir(data_dir_in='in_en_data_mcb64_50000',
                 data_dir_out='in_en_data_mcb32_50000',
                 mcb_tokenise_en=False,
                 fmax_size=lambda orig_size: orig_size // 32,
                 data_dir_orig='in_en_data_50000')
mcb_tokenise_dir(data_dir_in='in_en_data_mcb32_50000',
                 data_dir_out='in_en_data_mcb16_50000',
                 mcb_tokenise_en=False,
                 fmax_size=lambda orig_size: orig_size // 16,
                 data_dir_orig='in_en_data_50000')
mcb_tokenise_dir(data_dir_in='in_en_data_mcb16_50000',
                 data_dir_out='in_en_data_mcb8_50000',
                 mcb_tokenise_en=False,
                 fmax_size=lambda orig_size: orig_size // 8,
                 data_dir_orig='in_en_data_50000')


