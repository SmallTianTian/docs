# coding=utf-8

from urllib import request
from bs4 import BeautifulSoup as HtmlParse
import chardet

def getContent(url):
    with request.urlopen(url) as response:
        return response.read()

def getContentAndCharset(url):
    content = getContent(url)
    charset = chardet.detect(content)['encoding']
    return (content, charset)

def getUTF8Content(url):
    content, charset = getContentAndCharset(url)
    return content if charset == 'utf-8' else content.decode(charset).encode('utf-8')

def html(url):
    return HtmlParse(getUTF8Content(url))
