import redis
from exception import *

redis_expire_time = 600 #10 min

class for_redis:
	def __init__(self, logger, port):
		self.logger = logger
		r = redis.StrictRedis(port=port)
		if r.ping():
			logger.info('redis connect success')
			self.r = r
		else:
			logger.Exception('ping error')
			raise ping_error

	def set_result(self, k, v):
		self.r.set(k, v)
		self.r.expire('key1', redis_expire_time) 

	def get_result(self, k):
		return self.r.get(k)


