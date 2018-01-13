class MyType(type):
    def __init__(self,name,base=None,dict=None):
        print("init mytype")
        super(MyType,self).__init__(name,base,dict)
        
    def __call__(self,*args,**kwargs):
        print('call mytype')
        
class Test(object):
    __metaclass__ = MyType
    
    def __init__(self,name):
        self.name = name
        print("Test init")
        

obj = Test('king')