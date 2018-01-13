#-*-coding:utf-8-*-


selectdict = {'column':'','table':'','where':''}
insertdict = {'table':'','column':'','values':''}
deletedict = {'table':'','where':''}
updatedict = {'table':'','set':'','where':''}


def select(c):
    

def delRow(id)

def addRow():



def reloveCommand(command):
    c = command.split(' ')
    if c[0] == 'select':
        selectdict['column'] = c[1]
        selectdict['table'] = c[3]
        selectdict['where'] = c[5:len(c)]
        return selectdict
    elif c[0] == 'insert':
        insertdict['table'] = c[2]
        insertdict['column'] = c[3]
        insertdict['values'] = c[5:len(c)]
        return insertdict
    elif c[0] == 'delete':
        deletedict['table'] = c[2]
        deletedict['where'] = c[4:len(c)]
        return deletedict
    elif c[0] == 'update':
        updatedict['table'] = c[1]
        updatedict['set'] = c[3]
        updatedict['where'] = c[5:len(c)]
        return updatedict
    else:
        print "wrong command"

while True:
    command = raw_input('please input sql command:').strip()
    print reloveCommand(command)
    
    