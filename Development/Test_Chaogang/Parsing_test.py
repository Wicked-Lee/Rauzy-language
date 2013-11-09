#############################################################
##This is a simple test to use python to parse a jason file## 
##into a python object                                     ## 
#############################################################

import json

#define a "parse" function to parse a jason file into a python dict object
def parse(file):
	#open and then read the file
    f=open(file,'r')        #open a file for reading
    s=f.read()              #read the content of file f
	#To get rid of all the unmeSaning symbols after reading
    s=s.replace("\n","")    #replace the string "\n" by ""
    s=s.replace("\t","")    #replace the string "\t" by ""
    s=" ".join(s.split())   #remove the duplicated spaces
	#return a python object out of a jason object
    target=json.loads(s)
    f.close()
    return target

#load a json format file and get the corresponding python dict object
target=parse('Bank.rau')    

#Print the keys and the values of the dict object
keys=target['objects'].keys()
print(keys)
values=target['objects'].values()
print(values)

#Treat the special occassions(If the objects in "target" is "")
for key in keys:
    if target['objects'][key]=="":
        target1=parse(key+'.rau')#we look into the same file to find the component
        target['objects'][key]=target1
