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
    app.classList = classInherit
    app.subClassesInfo = subClassesInfo
    app.replaceList = replaceList
    return render_template('index.html', classInherit = app.classList, 
            subClassesInfoForJS = app.subClassesInfo, classInheritForJS = app.classList, rDict = app.replaceList)

@app.route('/set_default', methods = ['POST'])
def set_default():
    try:
        data = json.loads(request.data)
        with open(config_path + r'cfg.txt', 'wb') as f:
            pickle.dump(data, f)
        return json.dumps('success')
    except Exception as e:
        return json.dumps('error: ' + str(e))

@app.route('/texture/<path:filename>', methods = ['GET', 'POST'])
def send_pic(filename):
    return send_from_directory('./texture', filename)

def parseItem(key, value):
    anno = value['annotation']
    args = value['default']
    if anno == 'str' or anno[0] == '|':
        return args
    else:
        return json.loads(args)

def parseData(data):
    elementList = []
    for elem in data:
        if not elem:
            elementList.append(Identity())
        elif type(elem[0]).__name__ == 'str':
            classType = elem[0]
            for key, value in elem[1].items():
                elem[1][key] = parseItem(key, value)
            elementList.append(eval(classType + '(**elem[1])'))
        elif type(elem[0]).__name__ == 'list':
            tempElemList = parseData(elem)
            elementList.append(tempElemList)
    return elementList

@app.route('/show', methods = ['POST'])
def show():
    try:
        data = json.loads(request.data)
        print(data)
        elemList = parseData(data)
        elemList = [np.sum(i) for i in elemList]
        deleteImgs()
        [i.show(k) for (k, i) in enumerate(elemList)]
        return json.dumps('success')
    except Exception as e:
        return json.dumps('error: ' + str(e))

@app.route('/calc', methods = ['POST'])
def calc():
    try:
        data = json.loads(request.data)
        elemList = parseData(data)
        elemList = [np.sum(i) for i in elemList]
        np.product(elemList)
        deleteImgs()
        [i.show(k) for (k, i) in enumerate(elemList)]
        return json.dumps('success')
    except Exception as e:
        return json.dumps('error: ' + str(e))

def deleteImgs():
    files = os.listdir('texture\\')
    for fileName in files:
        os.remove('texture\\' + fileName)

if __name__ == '__main__':
    webbrowser.open_new_tab("http://127.0.0.1:8000")  
    app.run(port = 8000, debug = False)
