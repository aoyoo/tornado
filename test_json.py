#!/usr/bin/env python
# -*- coding=utf-8 -*-
import sys
import time
import json
import string
import copy 
import re
#reload(sys)
#sys.setdefaultencoding('utf-8')

raw_str = """[{"title":"title1", "price":"500"},{"title":"title2", "price":"441"}]"""
raw_list = [{"title":"啊啊啊", "price":"500"},{"title":"title2", "price":"441"}]

print raw_list

json1 = json.dumps(raw_list, encoding='utf-8')
#json2 = json.loads(raw_str)

print json1
print type(json1)

