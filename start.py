from flask import Flask, request, send_from_directory, jsonify, redirect
import db.classDB as database
import java.doc as java
import time
import _thread
import os

app = Flask(__name__)

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    return send_from_directory('static', './html/index.html')

@app.route('/<path:path>.html')
def html(path):
    return send_from_directory('static', './html/%s.html' % path)

@app.route('/<path:path>')
def docs(path):
    return send_from_directory('static', path)

@app.route('/all_project_name')
def allProjectName():
    data = database.searchAllProjectName()

    keys = ['id', 'name', 'version', 'enabled', 'language', 'iconHref']
    return jsonify([dict(zip(keys, line)) for line in data])

@app.route('/fuzzy_query/<string:projectId>/<string:key>')
def fuzzyQuery(key, projectId):
    #TODO -1? stupid
    data = database.searchDB(key, None if projectId == '-1' else projectId)
    keys = ['key_type', 'project_icon', 'key_id', 'sign_name', 'href']

    return jsonify([dict(zip(keys, line)) for line in data])

@app.route('/isDoc/<path:path>')
def isDoc(path):
    flag = True
    try:
        flag = java.isJavaDocAccordingUrl(path)
    except Exception as e:
        print(e)
        flag = False
    return jsonify({"result": flag})

@app.route('/createNewProjectTask', methods=['POST'])
def createNewProjectTask():
    url      = request.form['url']
    name     = request.form['name']
    version  = request.form['version']
    lang     = request.form['lang']
    icon     = request.files['iconhref']
    if not os.path.exists('./static/doc/%s/%s/' % (name, version)):
        os.mkdir('./static/doc/%s/%s/' % (name, version), 744)
    iconPath = './static/doc/%s/%s/project.png' % (name, version)
    icon.save(iconPath)

    # new thread to call function
    _thread.start_new_thread(java.createNewDocs, (url, name, version, lang, iconPath))
    return redirect('/manage.html')

@app.route('/enable/<string:key>/<string:enable>')
def enable(key, enable):
    flag = True
    try:
        database.projectEnable(key, enable)
    except Exception as e:
        print(e)
        flag = False
    return jsonify({"result": flag})

@app.route('/removeProject/<string:key>')
def removeProject(key):
    flag = True
    try:
        database.removeProject(key)
    except Exception as e:
        print(e)
        flag = False
    return jsonify({"result": flag})

@app.route('/detailed/<string:item>/<int:key>')
def detailed(item, key):
    data = database.detailed(item, key)
    c, m, f = data
    key = ['name', 'href']
    cj = [dict(zip(key, line)) for line in c]
    mj = [dict(zip(key, line)) for line in m]
    fj = [dict(zip(key, line)) for line in f]

    items = ('Constructors', 'Methods', 'Fields')
    return jsonify(dict(zip(items, (cj, mj, fj))))

if __name__ == '__main__':
    app.run()
