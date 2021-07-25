# -*- coding: utf-8 -*-
"""Copy of train.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1GEhw17xpm2sYFjxSzXUWbe7pazbgrWxY

# Check the gpu
1.  for tiny_model, tiny_plus_model only T4 and K80 are allowed.
2.  for big_model only P100, T4 and K80 are allowed.
"""

from IPython.display import HTML, clear_output
from subprocess import getoutput
s = getoutput('nvidia-smi')
if 'K80' in s:gpu = 'K80'
elif 'T4' in s:gpu = 'T4'
elif 'P100' in s:gpu = 'P100'
else:gpu='DONT PROCEED'
display(HTML(f"<h1>{gpu}</h1>"))

"""# Mount the drive and import necessary libraries"""

# Commented out IPython magic to ensure Python compatibility.
from google.colab import drive
from os import listdir, remove, makedirs
from os.path import join, exists
import random
drive.mount('/gdrive')
# %cd /gdrive/MyDrive/darknet
!chmod +x ./darknet
!./darknet

"""# Start Training from beginning
1.  No need to run below this, if you are going to **resume**. [Click here](#resume-cell) to go to the resume cell.
"""

# change this path
inputpath="overall_new"
if "gdrive" not in inputpath:
    inputpath = "/gdrive/MyDrive/"+inputpath
if exists(inputpath):
    x = input("Which model you want to train?\n\t1. tiny model\n\t2. tiny plus model\n\t3. big model\n")
    dont_run=False
    if x=='1':model_type = "tiny_model"
    elif x=='2':model_type = "tiny_plus_model"
    elif x=='3':model_type = "big_model"
    else:
        dont_run=True
        clear_output()
        print("Enter correct input among 1,2 and 3.")
else:
    print(inputpath, "cannot be found please correct it.")

"""### Helper Functions"""

def check_existence(folder, count=0):
    tmp="" if count==0 else "_"+str(count)
    check_folder = folder+tmp
    if (check_folder in listdir(".")) and (len([k for k in listdir(check_folder) if ".weights" in k])!=0):
        count+=1
        return check_existence(folder, count)
    else:
        return check_folder
def get_all_files(folder:str, result:dict):
    tmp = sorted(listdir(folder))
    result[folder]=[i for i in tmp if (".jpg" in i) or (".txt" in i)]
    for i in tmp:
        if "." not in i:
            get_all_files(join(folder, i), result)
def get_images_txt(folder:str):
    data = {}
    get_all_files(folder, data)
    del data[folder]
    final_data = {}
    for i in data.keys():
        if len(data[i])==0:
            continue
        class_ = i[len(folder)+1:].split("/")[0]
        if class_ not in final_data.keys():
            final_data[class_]={}
        final_data[class_][i] = []
        for j in range(len(data[i])-1):
            if data[i][j][:data[i][j].rfind('.')]==data[i][j+1][:data[i][j+1].rfind('.')]:
                final_data[class_][i].append([i+'/'+data[i][j], i+'/'+data[i][j+1]])
                j+=1
    return final_data

"""### Confirm the output folder"""

if not dont_run:
    clear_output()
    outputpath="_".join(inputpath.split("/")[3:])+"_"+model_type
    outputpath = check_existence(outputpath)
    print("Output folder is "+outputpath+".")
    x = input("Please confirm to create the output folder (y/n):")
    if x == 'y':
        if not exists(outputpath):
            makedirs(outputpath)
        print("Output folder created.")
    elif x == 'n':
        print("Output folder not created.")
    else:
        print("Please input valid character.")

"""### Confirm the count of images and classes.
1.  Those numbers tells the count of pair of image and it's annotation.
2.  Adjust the threshold value to increase and decrease the classes.
"""

threshold = 10
data = get_images_txt(inputpath)
key_list = sorted(list(data.keys()))
count=0
for i in key_list:
    l = sum([len(k) for k in data[i].values()])
    if l>threshold:
        print(count,i, l)
        count+=1
    else:
        del data[i]
x = input("Please confirm that classes and count of images are correct (y/n):")
if x == 'y':
    classes = sorted(data.keys())
    print("Classes selected.")
elif x == 'n':
    classes = None
    print("Classes not selected.")
else:
    classes = None
    print("Please input valid character.")

def clip_first(n, d):
    key_list = sorted(list(d.keys()))
    result = {i:[] for i in key_list}
    key_counter = {i:0 for i in key_list}
    prev = 0
    while True:
        for i in key_list:
            if key_counter[i]>=len(d[i]):
                continue
            else:
                result[i].append(d[i][key_counter[i]])
                key_counter[i]+=1
        x = sum([len(k) for k in result.values()])
        if x==prev:
            break
        prev = x
        if sum([len(k) for k in result.values()])>=n:
            break
    return result

key_list = sorted(list(data.keys()))
min_count=100000000
for i in key_list:
    l = sum([len(k) for k in data[i].values()])
    min_count = min(min_count, l)
print("Minimum number of images in a class:",min_count)
for i in key_list:
    data[i] = clip_first(min_count, data[i])
count = 0
for i in key_list:
    l = sum([len(k) for k in data[i].values()])
    print(count, i, l)
    count+=1
x = input("Please confirm that clipped count of images are correct (y/n):")
if x == 'y':
    classes = sorted(data.keys())
    print("Classes selected.")
elif x == 'n':
    classes = None
    print("Classes not selected.")
else:
    classes = None
    print("Please input valid character.")

for i in classes:
    print(i)
    for j in sorted(data[i].keys()):
        print(j, len(data[i][j]))
    print()

"""### Change ids in the annotation files
1.  This cell will take some time.
"""

for id in range(len(classes)):
    tmp = 0
    cls = classes[id]
    print(cls+"-", end = " ")
    for i in data[cls].keys():
        for j in data[cls][i]:
            f = open(j[1],'r')
            s = [k.split(" ") for k in f.read().split('\n')]
            s = [k for k in s if len(k)==5]
            s = [[str(id)]+k[1:] for k in s]
            s = "\n".join([" ".join(k) for k in s])+"\n"
            f.close()
            f = open(j[1],'w')
            f.write(s)
            f.close()
            tmp+=1
            if tmp%100==0:
                print(tmp, end=".. ")
    print(tmp)

"""### Save the training data"""

train=[]
for id in range(len(classes)):
    for i in data[classes[id]].keys():
        train.extend([k[0] for k in data[classes[id]][i]])
train=[i for i in train if ".txt" not in i]
random.shuffle(train)
l=len(train)
valid=train[int(l*5/6):]
train=train[:int(l*5/6)]
f=open(join(outputpath, model_type+"_train.txt"),'w')
f.write("\n".join(train))
f.close()
f=open(join(outputpath, model_type+"_valid.txt"),'w')
f.write("\n".join(valid))
f.close()

"""### Save the names file and data file"""

f=open(join(outputpath, model_type+"_obj.names"),'w')
f.write("\n".join(classes))
f.close()
numClass=len(classes)
objdata=["classes= "+str(numClass),
         "train = "+join(outputpath, model_type+"_train.txt"),
         "valid = "+join(outputpath, model_type+"_valid.txt"),
         "names = "+join(outputpath, model_type+"_obj.names"),
         "backup = "+outputpath+"/"]
f=open(join(outputpath, model_type+"_obj.data"),"w")
f.write("\n".join(objdata))
f.close()

"""### Copy the appropriate config file"""

import shutil
dest_cfg_name = model_type+"_yolov4.cfg"
if model_type == "tiny_model":
    src_cfg_name = "yolov4-tiny-custom.cfg"
    netSize=416
    batch=64
    subdiv=1
    max_batches_multiplier = 3000
    default_max_batch = 500200
elif model_type == "tiny_plus_model":
    src_cfg_name = "yolov4-tiny-custom.cfg"
    netSize=608
    batch=64
    subdiv=2
    max_batches_multiplier = 3000
    default_max_batch = 500200
elif model_type == "big_model":
    src_cfg_name = "yolov4-custom.cfg"
    netSize=416
    batch=64
    subdiv=16
    max_batches_multiplier = 2000
    default_max_batch = 500500
if dest_cfg_name not in listdir(outputpath):
    shutil.copy("cfg/"+src_cfg_name, outputpath+'/'+dest_cfg_name)
else:
    remove(outputpath+'/'+dest_cfg_name)
    shutil.copy("cfg/"+src_cfg_name, outputpath+'/'+dest_cfg_name)

"""### Configure the training details"""

#change number of class and filters
comm='s/classes=80/classes='+str(numClass)+"/"
!sed -i $comm $outputpath/$dest_cfg_name
comm='s/filters=255/filters='+str((numClass+5)*3)+"/"
!sed -i $comm $outputpath/$dest_cfg_name

#change number of steps and max batches
max_batches=max(6000,(numClass)*max_batches_multiplier)
comm='s/max_batches\ =\ '+str(default_max_batch)+'/max_batches\ =\ '+str(max_batches)+"/"
!sed -i $comm $outputpath/$dest_cfg_name
comm='s/steps=400000,450000/steps='+str(int(0.8*max_batches))+','+str(int(0.9*max_batches))+"/"
!sed -i $comm $outputpath/$dest_cfg_name

#can be multiple of 32 or 608(but makes training slow)
comm='s/width=416/width='+str(netSize)+"/"
!sed -i $comm $outputpath/$dest_cfg_name
comm='s/height=416/height='+str(netSize)+"/"
!sed -i $comm $outputpath/$dest_cfg_name

comm='s/batch=64/batch='+str(batch)+'/'
!sed -i $comm $outputpath/$dest_cfg_name
comm='s/subdivisions=1/subdivisions='+str(subdiv)+'/'
!sed -i $comm $outputpath/$dest_cfg_name

"""### Download the weight if doesn't exist"""

if "yolov4.conv.137" not in listdir():
    !wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.conv.137
if "yolov4-tiny.conv.29" not in listdir():
    !wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.conv.29

"""# Start the training
1.  if you are running from the top, then run the below cell directly.
2.  if you have done the configurations before hand, and want to run this cell, then define the outputpath variable in some other cell, and then run the below cell.
3.  outputpath variable contains the folder name in which model will be saved.
"""

obj_file = None
cfg_file = None

if "tiny_model" in outputpath : model_name = "yolov4-tiny.conv.29"
elif "tiny_plus_model" in outputpath : model_name = "yolov4-tiny.conv.29"
elif "big_model" in outputpath : model_name = "yolov4.conv.137"

for i in listdir(outputpath):
    if "obj.data" in i:
        obj_file = join(outputpath, i)
    elif ".cfg" in i:
        cfg_file = join(outputpath, i)

if obj_file == None:
    print(".data file not found in", outputpath)

if cfg_file ==None:
    print(".cfg file not found in", outputpath)

if (obj_file != None) and (cfg_file != None):
    !./darknet detector train $obj_file $cfg_file $model_name -dont_show -map

"""<a name="resume-cell"></a>
# Resume the training
1. For resuming the training process, it is complulsory to define the outputpath.
2.  outputpath variable contains the folder name in which model will be saved.
"""

outputpath = input("Write the outputpath where previous training was done?\n")
clear_output()

obj_file = None
cfg_file = None
last_weight = None
folder_exists = exists(outputpath)
if folder_exists:
    for i in listdir(outputpath):
        if "obj.data" in i:
            obj_file = join(outputpath, i)
        elif ".cfg" in i:
            cfg_file = join(outputpath, i)
        elif "last.weights" in i:
            last_weight = join(outputpath, i)
else:
    print(outputpath, "does not exist please check the name.")

if (obj_file == None) and (folder_exists):
    print(".data file not found in", outputpath)
if (cfg_file ==None) and (folder_exists):
    print(".cfg file not found in", outputpath)
if (last_weight ==None) and (folder_exists):
    print("last.weights file not found in", outputpath)

if (obj_file != None) and (cfg_file != None) and (last_weight != None):
    !./darknet detector train $obj_file $cfg_file $last_weight -dont_show -map

