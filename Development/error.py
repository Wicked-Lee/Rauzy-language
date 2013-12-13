#define a Error class to raise user-defined errors.
class error(Exception):
    #"msg" is the error message that we should print
    def __init__(self,msg):
        self.msg=msg
    #the fonction to print the error message
    def toStr(self):
        print(self.msg)

