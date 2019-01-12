#coding:utf-8

import os
import shutil

def saveToSpecificPath(path, content):
    reallyPath = path[0 : path.rindex('/')]
    if not os.path.exists(reallyPath):
        os.makedirs(reallyPath)
    with open(path, 'wb') as f:
        print('save to %s.' % path)
        if isinstance(content, str):
            f.write(content.encode())
        else:
            f.write(content)

def checkFileExist(path):
    return os.path.isfile(path)

def saveContent(content):
    raise Exception('No realize.')

def cleanProject(path):
    shutil.rmtree('/folder_name')
