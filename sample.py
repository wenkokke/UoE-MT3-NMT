import math
import random as rn
import numpy as np
cnt = 0
eng_smpl = open("eng_sample.txt.txt",'w',encoding="utf8")
fr_smpl = open("fr_sample.txt.txt",'w',encoding="utf8")
rdn = rn.sample(range(2000000),50000)
print(len(rdn))
print(rdn)
line_cnt = 0
with open("europarl-v7.fr-en.en",encoding="utf8") as english:
    with open("europarl-v7.fr-en.fr",encoding="utf8") as french:
        for line_E,line_F in zip(english,french):
            line_cnt += 1

            if line_cnt in rdn:
                print(line_cnt)
                eng_smpl.write(line_E)
                fr_smpl.write(line_F)



