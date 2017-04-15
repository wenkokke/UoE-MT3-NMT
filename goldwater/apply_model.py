
# coding: utf-8

# In[4]:

import getopt
import itertools
import json
import sys


# In[2]:

def apply_model(model_file,data_file_in,data_file_out):
    
    with open(model_file, 'r') as model_file:
        model = json.load(model_file)
        
    with open(data_file_in, 'r') as text_raw:
        text_raw = text_raw.readlines()
        
    assert len(model) == len(''.join(line.rstrip() for line in text_raw))
    
    with open(data_file_out, 'w') as text_out:
        start = 0
        for line_raw in text_raw:
            line = ""
            for char in line_raw.rstrip():
                line += char
                if model[start] == 1:
                    line += ' '
                start += 1
            text_out.write(line + '\n')


# In[5]:

def usage():
    print("usage: apply_model -i INPUT_FILE -o OUTPUT_FILE -m MODEL_FILE")

if __name__ == "__main__":
    try:
        opts,args = getopt.getopt(sys.argv[1:],'i:o:m:',['input','output','model'])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    data_file_in,data_file_out,model_file = None,None,None
    for o,a in opts:
        if o in ['-i', '--input']:
            data_file_in = a
        if o in ['-o', '--output']:
            data_file_out = a
        if o in ['-m', '--model']:
            model_file = a
    if data_file_in and data_file_out and model_file:
        apply_model(model_file,data_file_in,data_file_out)
    else:
        usage()


# In[ ]:



