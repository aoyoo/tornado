# -*- coding=utf-8 -*-
import tornado.ioloop
import tornado.web
import tornado.httpclient

import requests
import redis

import time, json, thread
import log, for_tts, for_redis
from exception import *

logger = log.log()

r = for_redis.for_redis(logger, 6379)

def run(tor):
	#print tor.request.headers
	request_index = tor.request.headers.get("request_index")
	item_count_per_page = tor.request.headers.get("item_count_per_page")
	class_id = tor.request.headers.get("category")
	image_md5 = tor.request.headers.get("image_md5")

	if class_id == None or request_index == None or item_count_per_page == None or image_md5 == None:
		logger.error("bad request")
		tor.set_status(400)
		tor.finish()
		return

	try:
		request_index = int(request_index)
		item_count_per_page = int(item_count_per_page)
		class_id = int(class_id)
	except Exception, data:
		logger.error("bad request num %s " % data)
		tor.set_status(400)
		tor.finish()
		return
	
	if request_index == 0: #new image
		image_content = tor.request.body
		if image_content == None:
			logger.error("image content error")
			tor.set_status(400)
			tor.finish()
			return
		item_list = for_tts.postTTS(logger, class_id, image_content)
		if item_list != None:
			try:
				#global r
				#r.set_result(image_md5, str(item_list)) # set value is str
				r.set_result(image_md5, json.dumps(item_list,ensure_ascii=False)) # set value is str
			except Exception, data:
				logger.error("redis set_result error %s" % data)
				tor.set_status(400)
				tor.finish()
				return
		else:
			logger.debug("get no result")
			return_dict = { 'count' : 0,
					}
			tor.write(json.dumps(return_dict))
			tor.finish()
			return
			
		#just write tts_result by 1 ~ item_count_per_page 
		item_num = len(item_list)
		return_dict = { 'count' : 0,
						'price_max' : 0,
						'price_min' : 0,
						'content' : []
					}
		return_dict['count'] = item_num
		item_list_price_sorted = sorted(item_list, key = lambda x: x['price'])
		return_dict['price_min'] = item_list_price_sorted[0]['price']
		return_dict['price_max'] = item_list_price_sorted[-1]['price']
		#return_list = []
		return_num = item_count_per_page
		if item_num < item_count_per_page:
			return_num = item_num
		for i in range(return_num):
			#return_list.append(item_list[i])
			return_dict['content'].append(item_list[i])
	
		#tor.write(json.dumps(return_list,ensure_ascii=False))
		tor.write(json.dumps(return_dict,ensure_ascii=False))
		tor.finish()
		return
	else: 
		try:
			tts_result = r.get_result(image_md5)
		except Exception, data:
			logger.error("redis get_result error %s" % data)
			tor.set_status(400)
			tor.finish()
			return

		if tts_result == None:
			logger.error("redis get_result None")
			tor.set_status(400)
			tor.finish()
			return
			
		item_list = json.loads(tts_result)
	
		#just write tts_result by item_count_per_page*request_index ~ item_count_per_page*(request_index+1)
		item_num = len(item_list)
		return_dict = { 'content' : []
					}
		#return_list = []
		return_start_num = item_count_per_page*request_index
		return_end_num = item_count_per_page*(request_index+1)
	
		if item_num < return_start_num: #no more any result
			logger.error("no more any result item_num %s start num %s" % (item_num, return_start_num))
			tor.set_status(400)
			tor.finish()
			return
		if item_num < return_end_num:
			return_end_num = item_num

		for i in range(return_start_num, return_end_num):
			#return_list.append(item_list[i])
			return_dict['content'].append(item_list[i])
		#tor.write(str(return_list))
		tor.write(json.dumps(return_dict))
		tor.finish()
	
class MainHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def post(self):
		thread.start_new_thread(run, (self,))  
	
application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
	application.listen(8000)
	tornado.ioloop.IOLoop.instance().start()



