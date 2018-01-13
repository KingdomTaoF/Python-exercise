import abc
 
class Alert(object):
    '''报警基类'''
    __metaclass__ = abc.ABCMeta
 
    @abc.abstractmethod
    def send(self):
        '''报警消息发送接口'''
        pass
 
 
 
class MailAlert(Alert):
    pass
 
 
m = MailAlert()
m.send()