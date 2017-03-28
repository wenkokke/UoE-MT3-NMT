"""""
import fileinput
def charac(file):
    with fileinput.FileInput(file, inplace=True,backup='.bak') as files:
        for line in files:
            line = line.strip()
            tokens = line.split()
            for token in tokens:
                print(token.replace("", " ")[1: -1])

eng_smpl = open("eng_sample.txt.txt",'r',encoding="utf8")
fr_smpl = open("fr_sample.txt.txt",'r',encoding="utf8")
#charac("eng_sample.txt.txt")
charac("fr_sample.txt.txt")
"""""
# Read in the file
with open('text.en', 'r',encoding="utf8") as file :
  filedata = file.read()

# Replace the target string
filedata = filedata.replace('', ' ')

# Write the file out again
with open('text.en', 'w',encoding="utf8") as file:
  file.write(filedata)