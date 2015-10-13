from class_def import *
from flask import Flask, session, render_template, request, json, send_from_directory
from jinja2 import Environment, PackageLoader
import copy
import time
import pickle
import webbrowser  
import os

app = Flask(__name__)
app.jinja_env.line_statement_prefix = '#'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1
config_path = 'config/'

@app.route('/')
def init():
    app.elementList = []
    app.classList = classInherit
    app.classListForJS = classInheritForJS
    app.baseClassType = baseClassType
    app.replaceList = replaceList
    return render_template('index2.html', classInherit = app.classList, classInheritForJS = app.classListForJS, rDict = app.replaceList)

@app.route('/set_default', methods = ['POST'])
def set_default():
    data = json.loads(request.data)
    print(data)
    with open(config_path + r'cfg.txt', 'wb') as f:
        pickle.dump(data, f)
    return 'success'

@app.route('/add', methods = ['POST'])
def add():
    data = json.loads(request.data)
    classType = data['type']
    group = data['group']
    del data['type']
    del data['group']
    if group == 0:
        for key, value in data.items():
            if key in ['imgPath', 'express']:
                data[key] = value
            else:
                data[key] = eval(value)
        print(data)
        app.elementList.append(eval(classType + '(**data)'))
        try:
            '''
            deleteImgs()
            calc(app.elementList)
            '''
            t = app.elementList[-1]
            return json.dumps([type(t).__name__, t.toDict()])
        except TypeError as e:
            del app.elementList[-1]
            return json.dumps(['error', str(e)])
    elif group == 1:
        app.elementList.append([])
        return json.dumps('a')
    elif group == 2:
        for key, value in data.items():
            data[key] = eval(value)
        print(data)
        app.elementList[-1].append(eval(classType + '(**data)'))
        try:
            '''
            deleteImgs()
            calc(app.elementList)
            '''
            t = app.elementList[-1][-1]
            return json.dumps([type(t).__name__, t.toDict()])
        except TypeError as e:
            del app.elementList[-1][-1]
            return json.dumps(['error', str(e)])
    elif group == 3:
        return json.dumps('a')
    
    
@app.route('/change', methods = ['POST'])
def change():
    data = json.loads(request.data)
    classType = data['type']
    idx = data['idx']
    del data['type']
    del data['idx']
    for key, value in data.items():
        if key in ['imgPath', 'express']:
            data[key] = value
        else:
            data[key] = eval(value)
    print(data)
    if len(idx) == 1:
        app.elementList[idx[0]] = eval(classType + '(**data)')
        '''
        deleteImgs()
        calc(app.elementList)
        '''
        t = app.elementList[idx[0]]
    elif len(idx) == 2:
        app.elementList[idx[0]][idx[1]] = eval(classType + '(**data)')
        '''
        deleteImgs()
        calc(app.elementList)
        '''
        t = app.elementList[idx[0]][idx[1]]
    return json.dumps([type(t).__name__, t.toDict()])

@app.route('/del', methods = ['POST'])
def delete():
    data = json.loads(request.data)
    if len(data) == 1:
        del app.elementList[data[0]]
    elif len(data) == 2:
        del app.elementList[data[0]][data[1]]
        if len(app.elementList[data[0]]) == 0:
            del app.elementList[data[0]]
    if app.elementList:
        '''
        deleteImgs()
        calc(app.elementList)
        '''
    return 'a'

@app.route('/texture/<path:filename>', methods = ['GET', 'POST'])
def send_pic(filename):
    return send_from_directory('./texture', filename)

def calc(elemList):
    print(elemList)
    clist = copy.deepcopy(elemList)
    clist = [np.sum(i) for i in clist]
    np.product(clist)
    [i.show(k) for (k, i) in enumerate(clist)]

def deleteImgs():
    files = os.listdir('texture\\')
    for fileName in files:
        os.remove('texture\\' + fileName)

if __name__ == '__main__':
    #webbrowser.open_new_tab("http://127.0.0.1:8000")  
    app.run(port = 8000, debug = True)
