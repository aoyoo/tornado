#!/usr/bin/env python
# -*- coding=utf-8 -*-

import requests
import time
import json
import threading
import datetime

url = 'http://127.0.0.1:8000'

#if request_index, body is image_data + md5
#else body is just md5
head = {
	#"category":70020,
	"request_index":0,
	"item_count_per_page":10,
	"image_md5":""
	}
head["image_md5"] = time.time()

image_file = open('10086.jpg', 'rb')
image_data = image_file.read()
image_file.close()

r = requests.post(url, headers=head, data=image_data)

if r.status_code == 200:
	print head["image_md5"]
	r.encoding = 'utf-8'
	print r.text
else:
	print "ERROR ", r

#{'status':0,'content':[{'title':'title1', 'price':'500'},{'title':'title2', 'price':'441'}]}


