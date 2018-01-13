class Dog(object):
    def __init__(self,name):
        self.name = name
        
    @staticmethod
    def get():
        print('get name')
        
    @classmethod
    def eat(self):
        print('eating')
        
    @property
    def echo(self):
        print('name is: %s' % self.name)
        
d1 = Dog('xiaoming')
d1.get()
Dog.get()
d1.eat()
Dog.eat()
d1.echo

import os
print("%s:%s" %("file",'tet'))
