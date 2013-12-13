#define a warning class to raise user-defined Warnings.
class warning(Exception):
    #"msg" is the warning message that we should print
    def __init__(self,msg):
        self.msg=msg
    #the fonction to print the warning message
    def toStr(self):
        print(self.msg)

