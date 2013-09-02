#!/usr/bin/env python
# -*- coding=utf-8 -*-

import time, datetime, json, threading, thread

def threadFun(num):
	print "threadFun %s" % num
	
class ThreadClass(threading.Thread):
	def __init__(self, func, argv):
		#threading.Thread.__init__(self)  
		self.func = func 
		self.argv = argv
		
	def run(self):
		self.func(self.argv)
		#now = datetime.datetime.now()
		#print "%s time %s argv %s" % (self.getName(), now, self.argv)
	
class ThreadPoolClass:
	def __init__(self, num):
		if num <= 0:
			raise Exception, 'thread number error %s' % num
		self.threadNum = num
		self.threadArray = []
		for i in range(self.threadNum):
			self.threadArray.append(ThreadClass(threadFun, i))
		
	def start(self):
		for ithread in self.threadArray:
			ithread.start()
	
	def join(self):
		for ithread in self.threadArray:
			ithread.join()
	
def main():
	t = ThreadPoolClass(5)
	t.start()
	t.join()

if __name__ == "__main__":
	main()


