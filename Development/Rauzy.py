import json
import os
import pprint
from Object import *
from Relation import *
from error import *
from warning import *

#define a "parse" function to parse a rau file for a model and create all Objects and Relations
def dupe_checking_hook(pairs):
    result = dict()
    for key,val in pairs:
        try:
            if key in result:
                raise error('Error 07:Redundant definition of '+key+'!\n')
            result[key] = val
        except error as e:
            e.toStr()
    return result

def parse(file):
        Object.folder = ""
        Object.model = False
        Relation.model = False
        model = None
        #open and then read the file
        err_str=''
        war_str=''
        list_obj=[]
        list_rel=[]
        f=open(file,'r')        #open a file for reading
        s=f.read()              #read the content of file f
        #To get rid of all the unmeaningful symbols after reading
        s=s.replace("\n","")    #replace the string "\n" by ""
        s=s.replace("\t","")    #replace the string "\t" by ""
        s=" ".join(s.split())   #remove the duplicated spaces
        f.close()
        #return a python object out of a json object
        #with object_pairs_hook method, we can check "Error 07" at the same level
        target=json.loads(s,object_pairs_hook=dupe_checking_hook)
        if "library" in target.keys():
                lib=''
                folders=file.split("/")
                for i in range(0,len(folders)-1):
                        lib+=folders[i]+"/"
                lib+=target['library']
                #To handle all the errors and warnings in "library" json file
                valstr=Object.readLibrary(lib)
                err_str+=valstr[0]
                war_str+=valstr[1]
                list_obj=valstr[2]
                list_rel=valstr[3]
        #To handle all the errors and warnings in "root" json file
        rootobj=[]
        rootrel=[]
        valstr2=val_root(file,target,True,list_obj,list_rel,rootobj,rootrel)
        err_str+=valstr2[0]
        war_str+=valstr2[1]
        try:
                if err_str != "":
                        raise error(err_str)
                else:
                        Object.model = True
                        Relation.model = True
                        model = Object(file.split(".")[0],target)
                        if not Object.comp:
                            Object.flatten(rootobj,rootrel)
        except error as e:
                e.toStr()
        try:
                if war_str != "":
                        raise warning(war_str)
        except warning as w:
                w.toStr()
    #TO return the constructed model
        return model

#writes the necessary files for this model
#One file for root object
#One file (library) for the rest objects
def toFile(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
#export .rau file
    f = open(folder+'/'+model.name+'.rau','w')
    f.write(model.toJson(""))
#export library file
    lib = open(folder + '/'+model.library,'w')
    library = "{\n \"nature\" : \"library\", \n \"objects\" : \n{\n"
    for obj in Object.objectsLib:
        library += "\t\""+obj+"\" : \n" + Object.objectsLib[obj].toJson("\t") +",\n"
    library = library[:-2] + "\n"
    library += "\t},\n \"relations\" : \n {\n"
    for rel in Object.relationsLib:
        library += Object.relationsLib[rel].toJson("\t") + ",\n"
    library = library[:-2]
    library += "\n}\n}"
    lib.write(library)


#handle "Error 01: xx in the xx not defined!"
#handle "Error 05:the nature of xx != correct!"
#handle "Error 07:Redundant definition of xx!"
#handle "Warning 02:Detect of a library member in xx, but xx is not the root object."
#handle "Warning 03: [objects] and [relations] in object A will be overriden by these of object B as A extends B"
#tarname is name of the object(not necessarily the root object), target is the parsed file, "isroot" to signify the object is the root object or not
def val_root(tarname,target,isroot,list_obj,list_rel,rootobj,rootrel):
    err_str=""
    war_str=""
    #Type checking
    Type=Object.val_type(tarname,target)
    if Type[1]:
        err_str+=Type[0]
    else:
        if 'nature' not in target.keys() or target['nature']=='':
            err_str+='Error 01: the field [nature] is not defined in the object '+tarname+'!\n'
        elif target["nature"] != "object":
            err_str+='Error 05:the nature of object '+tarname+' is not correct!\n'
        if 'extends' in target.keys() and target['extends'] != '':
            if target['extends'] not in list_obj and 'Error 02' not in list_obj:
                err_str+=("Error 03: the object "+target['extends']+"extended in the root file is not defined !\n")
            if 'objects' in target.keys():
                #target.pop("objects",None)
                #print("after pop",target.keys())
                war_str+='Warning 03: "objects" in object '+tarname+' will be overriden by these of object '+target['extends']+' as '+tarname+'extends'+target['extends']+'\n'
        if 'objects' in target.keys() and target['objects'] != '':
            for key in target['objects'].keys():
                #with below, we can check "Error 07" at the different levels
                if key in list_obj:
                    err_str+='Error 07:Redundant definition of object '+key+'!\n'
                else:
                    list_obj.append(key)
                    rootobj.append(key)
                valstr=val_root(key,target['objects'][key],False,list_obj,list_rel,rootobj,rootrel)
                err_str+=valstr[0]
                war_str+=valstr[1]
        if isroot and 'relations' in target.keys() and target['relations'] != '':
            ##print('List of relations:\n',list_rel)
            for key in target['relations'].keys():
                rootrel.append(key)
                #Type checking
                Type1=Object.val_type(tarname+'[relations]['+key+']',target['relations'][key])
                if Type1[1]:
                    err_str+=Type1[0]
                else:
                    if 'nature' not in target['relations'][key]:
                        err_str+='Error 01: the field [nature] is not defined in root[relations]'+key+']\n'
                    elif target['relations'][key]['nature'] != 'relation':
                        err_str+='Error 05:the nature of'+tarname+'[relations]['+key+'] is not correct!\n'
                    if 'from' not in target['relations'][key] or target['relations'][key]['from']==[]:
                        err_str+='Error 01: the field [from] is not defined in '+tarname+'[relations]['+key+']\n'
                    else:
                        for fr in target['relations'][key]['from']:
                            if fr not in list_obj:
                                err_str+='Error 03: the object '+fr+' in the field '+tarname+'[relations]['+key+'][from] is not defined !\n'
                    if 'to' not in target['relations'][key] or target['relations'][key]['to']==[]:
                        err_str+='Error 01: the field [to] is not defined in '+tarname+'[relations]['+key+']\n'
                    else:
                        for fr in target['relations'][key]['to']:
                            if fr not in list_obj:
                                err_str+='Error 03: the object '+fr+' in the field '+tarname+'[relations]['+key+'][to] is not defined!\n'
                    if 'extends' in target['relations'][key] and target['relations'][key]['extends']!='':
                        if target['relations'][key]['extends'] not in list_rel and 'Error 02' not in list_obj:
                            err_str+=("Error 04: the relation "+target['relations'][key]['extends']+" is not defined !\n")
                    elif 'directional' not in target['relations'][key]:
                            err_str+='Error 01: the field [directional] is not defined in '+tarname+'[relations]['+key+']\n'
        if 'library' in target.keys() and target['library']!='' and not isroot:
            war_str+='Warning 02:Detect of a library member in'+tarname+',but '+tarname+' is not the root object\n'
    return err_str,war_str

#prints the model in screen
def printModel():
    print (model.toStr(""))

def flattenModel():
    print()
    print('*'*80+'\n'+'Flattened objects:\n')
    for obj in Object.flatObj.keys():
        print(obj,':')
        print(Object.flatObj[obj].toStr2("",'flat'))
    print('*'*80+'\n'+'Flattened relations:\n')
    for rel in Object.flatRel.keys():
        print(rel,':')
        print(Object.flatRel[rel].toStr(""))

def abstractModel(level):
    print(model.toStr2('',"abstract "+str(level)))

def modifyModel(field,newvalue):
    dest=field.split('.')
    nl=0
    key=None
    #The first element is always the nature of the object
    if dest[nl]=='object':
        key=Object.findObject(dest[nl+1])
        nl=nl+2
    elif dest[nl]=='relation':
        key=Object.findRelation(dest[nl+1])
        nl=nl+2
    elif dest[nl]=='library':
        if dest[nl+1]=='object':
            key=Object.findLibObject(dest[nl+2])
        elif dest[nl+1]=='relations':
            key=Object.findLibRelation(dest[nl+2])
        else:
            print('There is no '+dest[nl+1]+' field in the library!')
            return
        nl=nl+3
    else:
        print('The first field name is not recognized!')
        return
    #If we want to change the parent, we will change the string "extends"
    if dest[nl]=='extends':
        key=key.parent
        key.parent=newvalue
        nl+=1
    #If we want to change properties, we will change one of its properties
    elif dest[nl]=='properties':
        key=key.properties
        key[dest[nl+1]]=newvalue
        nl=nl+2
    #If we want to change 'relations', we will change the name of the relation
    elif dest[nl]=='relations':
        key=key.relations
        key.remove(dest[nl+1])
        key.append(newvalue)
    #If we want to change 'objects', we will change the name of the object
    elif dest[nl]=='objects':
        key=key.objects
        key.remove(dest[nl+1])
        key.append(newvalue)
    else:
        print('The field name is not recognized !')
        return

def compareModels():
    if Object.objects2:
        list_obj=[]
        list_rel=[]
        for obj in Object.objects:
            for obj2 in Object.objects2:
                if obj==obj2:
                    list_obj={}
    else:
        print('The second model does not exist !')

def checkModel(name):
    if name=='model':
        print(model.__str__())
    elif name=='objects':
        for obj in Object.objects.keys():
            print(obj+":",Object.objects[obj].__str__())
    elif name=='relations':
       for rel in Object.relations.keys():
            print(obj+":",Object.relations[rel].__str__())
    elif name=='objectsLib':
        for obj in Object.objectsLib.keys():
            print(obj+":",Object.objectsLib[obj].__str__())
    elif name=='relationsLib':
        for rel in Object.relationsLib.keys():
            print(obj+":",Object.relationsLib[rel].__str__())
    elif name=='objects2':
        for obj in Object.objects2.keys():
            print(obj+":",Object.objects2[obj].__str__())
    elif name=='relations2':
       for rel in Object.relations2.keys():
            print(obj+":",Object.relations2[rel].__str__())
    elif name=='objectsLib2':
        for obj in Object.objectsLib2.keys():
            print(obj+":",Object.objectsLib[obj].__str__())
    elif name=='relationsLib2':
        for rel in Object.relationsLib2.keys():
            print(obj+":",Object.relationsLib[rel].__str__())
    else:
        print('The object to be check is not recognized!')

#root Object
##model = parse("Bank.rau")
model = None
model2=None #Another model to compare
print ('type \'help\' for help')
input1=input('>>')
#input1 = raw_input('>>')
while(input1!='exit'):
    if input1.startswith('read') and not input1.startswith('read2'):
        Object.objects = dict()
        Object.relations = dict()
        Object.objectsLib = dict()
        Object.relationsLib = dict()
        if len(input1.split()) != 2:
            print ('usage: read <file name>')
        else :
            file = input1.split()[1]
            if not os.path.exists(file):
                print ('file \'' + file + '\' does not exist!')
            else:
                model = parse(file)
    elif input1.startswith('read2'):
        if model:
            print('Read another model for comparaison')
            Object.comp=True
            Relation.comp=True
            Object.objects2 = dict()
            Object.relations2 = dict()
            Object.objectsLib2 = dict()
            Object.relationsLib2 = dict()
            Relation.relations2=dict()
            if len(input1.split()) != 2:
                print ('usage: read <file name>')
            else :
                file = input1.split()[1]
                if not os.path.exists(file):
                    print ('file \'' + file + '\' does not exist')
                else:
                    model2=parse(file)
            Object.comp=False
            Relation.comp=False
    elif input1 == "help":
        print ("Available commands")
        print ('read <file name> \t to load the basic model')
        print('read2 <file name>  \t to load the second model for comparaison')
        print ('save <folder name> \t to save the basic model in a file')
        print ('print \t\t\t to print the basic model in the screen')
        print('abstract <level>\t to abstract the basic model to a certain level(integer)')
        print('flatten\t\t\t to flatten the basic model')
        print('compare\t\t\t to compare the basic model and the second model')
        print('modify\t\t\t to modify the basic model')
        print ('exit \t\t\t to exit')
    elif input1 == 'print':
        if model:
            printModel()
    elif input1.startswith('save'):
        if model:
            if len(input1.split()) != 2:
                print ('usage: save <folder name>')
            else:
                folder = input1.split()[1]
                toFile(folder)
    elif input1=='flatten':
        if model:
            flattenModel()
    elif input1=='compare':
        if model and model2:
            compareModels()
        elif model:
            print('The model for comparaison is not loaded ! Use "read2 <filename>" to load it !')
        else:
            print('The basic model is not loaded ! Use"read <filename>" to load it !')
    elif input1.startswith('abstract'):
        if model:
            if len(input1.split())!=2:
                print ('usage:abstract <level of abstraction>')
            else:
                abstractModel(input1.split()[1])
    elif input1=='modify':
        if model:
            field=input('Field to be modified(use "." as separator): ')
            newfield=input('The new value: ')
            commit=input('Commit the changes?(y/n): ')
            if commit=='y':
                modifyModel(field,newfield)
    #reserved for debugging
    elif input1.startswith('check'):
        pw=input('enter the password:')
        if pw=='checkmodel':
            if model:
                if len(input1.split())!=2:
                    print('usage:check <name>(objects,relations, objectsLib,relationsLib,model)')
                else:
                    checkModel(input1.split()[1])
        else:
            print('incorrect password!')
    else :
        print('Function not recognized!')
        print ('type \'help\' for help')

    if not model:
        print('The basic model is not loaded ! load a model with "read <filename>" !')
    input1=input('>>')
    #input1 = raw_input('>>')

####################################################################################
#############################
#To test Errors and Warnings#
#############################
##To test Error01-Error08
##print('*'*80+'\nBegin to test!\n'+'*'*80+'\n')
##for i in ['1','2','3','4','5','6','7','8']:
##    file='Test_python/Test_Error0'+i+'/Bank.rau'
##    target=parse(file)
##    print('*'*80+'\nTest_error0'+i+' finished!\n'+'*'*80+'\n')
####To test Warnings
##file="Test_python/Test_Warnings/Bank.rau"
##target=parse(file)
##print('*'*80+'\nTest_Warnings finished!\n'+'*'*80+'\n')
####To test Error00
##file0='Test_python/Test_Error00/Bank.rau'
##target=parse(file0)
##print('*'*20+'The first level analysis finished'+'*'*20+'\n')
##file1='Test_python/Test_Error00/Bank1.rau'
##target=parse(file1)
##print('*'*20+'The second level analysis finished'+'*'*20+'\n')
##file2='Test_python/Test_Error00/Bank2.rau'
##target=parse(file2)
##print('*'*20+'The third level analysis finished'+'*'*20+'\n')
##print('*'*80+'\nTest_Error00 finished!\n'+'*'*80+'\n')
####################################################################################
#model = parse("Bank.rau")
#printModel()
#print model.toJson("")

#print Object.objects
#print Object.relations
#print model["objects"]


