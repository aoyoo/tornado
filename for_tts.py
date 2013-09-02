# -*- coding=utf-8 -*-
import requests
import time
import json
import re
import copy
import sys
reload(sys)
sys.setdefaultencoding('utf8')

#url = 'http://10.0.0.239:6012'
#url = 'http://10.0.0.155:6011'
url = 'http://10.0.0.212:6007'

def get_value_from_string(str, key_str):
	pos = str.find(key_str) 
	value = '0'
	if pos != -1:
		pos = pos + len(key_str)
		pos1 = str.find(':',pos)
		pos2 = str.find(',',pos1)
		if pos2 == -1:
			pos2 = str.find('}',pos1)
			value = str[pos1+1:pos2]
		elif str[pos1+1:pos2-1].find('\"') == -1:
			value = str[pos1+1:pos2]
		else:
			value = str[pos1+2:pos2-1]
		#value.strip('\"')
	return value

ttk_gf_simi = 100
ttk_lf_simi = 84
ttk_lf_num = 20

#return None if error
#else return result list
def postTTS(log, cid, image_data):

	head = {
			'classId': '70020',
			'b2c_flag': '2',
			'color':'10',
			'gf': '100',
			'lf': '100',
			'tv': '0',
			'merge_same': '0',
			'text_count': '1',
			'text_type': '1',
			'gidORiid': '3',
			'text': '',
	
			'sortField':'creditGrade',
			'sortType':'1', 
	
			'groupSort':'',
			'gsType':'',
			'maxProPerGroup':'200',
	
			'version':'420',
			'command':'420',
			'src':4,
			'dest':'2222',
	
			'leftTop-x':'100',
			'leftTop-y':'1',
			'rightButtom-x': '300',
			'rightButtom-y':'3',
	
			'colorScore':'',
			'gfScore':'',
			'lfScore':'',
			'tvScore':'',
			'isMerge':'1',
			'productFeature': ''}
			
	head['classId'] = cid
	
#	image_file = open('290.jpg', 'rb')
#	image_data = image_file.read()
	
#	image_url = image_path
#	log.debug('start get image %s ' % image_url)
#	image_r = requests.get(image_url)
#	log.debug('get image len %s' % len(image_r.content))
#	r = requests.post(url, headers=head, data=image_r.content)
	r = requests.post(url, headers=head, data=image_data)
	
	if r.status_code == 200:
		r.encoding = 'utf-8'
		raw_str = r.text
		#raw_list = r.text.split('\n')
		raw_list = re.split('\n', raw_str)
		feat_list = []
		source_list = []
		group_num_list = []
		source = ['cf', 'gf', 'lf', 'tv']
		source_count = -1
		for line in raw_list:
			if line == '#':
				source_count += 1
				continue
			elif line == '' or line == '\n' or line == '\r' or line == '\n\r' or line == None:
				continue
			else:
				start_num = line.find(':')
				if start_num == -1:
					continue
				#line[start_num+1:]  #  {};{};
									#  {};{};#
				gid = line[0:start_num]
				line_without_gid = line[start_num+1:]
				if len(line_without_gid) < 10: #this gid without pinfo
					continue
				list_without_gid = line_without_gid.split('};{')
				num = len(list_without_gid)
				if num == 0:
					continue
				elif num == 1:  #only one
					#feat_list.append(line_without_gid[:-1].encode('utf-8'))
					feat_list.append(line_without_gid[:-1])
					source_list.append(source[source_count])
					group_num_list.append(1)
					continue
				else:
					feat_list.append(list_without_gid[0] + '}') #append first pid info
					source_list.append(source[source_count])
					group_num_list.append(len(list_without_gid))
					for tmp_line in range(1, num-1):
						feat_list.append('{' + list_without_gid[tmp_line] + '}')
						source_list.append(source[source_count])
					feat_list.append('{' + list_without_gid[-1][:-1]) #append last pid info
					source_list.append(source[source_count])
					continue
				
		log.debug('TTS feat result len: %s' % len(feat_list))
		result_list = []
		same_num = 0
		list_index = 0
		pid_dict = {}
		feat_list_num = len(feat_list)
		for i in range(feat_list_num):
			item = {}
			pid = get_value_from_string(feat_list[i],'id')
			item['pid'] = pid
			item['title'] = get_value_from_string(feat_list[i],'productTitle'.encode('utf-8'))
			item['product_url'] = get_value_from_string(feat_list[i],'url')
			item['simi'] = get_value_from_string(feat_list[i],'similarity')
			item['image_url'] = get_value_from_string(feat_list[i],'mainViewImagePath')
			item['price'] = get_value_from_string(feat_list[i],'price')[:-2]
			#item['sales'] = get_value_from_string(feat_list[i],'salesVolume')
			item['source'] = source_list[i]
			result_list.append(item)
		log.debug('TTS result list len: %s' % len(result_list))
	
		if len(result_list) == 0:
			return None
	
		#result_item_templete = "{'title':'%s', 'price':'%s', 'product_url':'%s', 'image_url':'%s', 'simi':'%s', 'source':'%s'}"
		result_item_templete = {'title':'', 'price':'', 'product_url':'', 'image_url':'', 'simi':'', 'source':''}
		return_list = []
	
		return_lf_num = 0
		for item in result_list:
			tmp_return_item = copy.copy(result_item_templete)
			tmp_return_item['title'] = item.get('title').encode('utf-8')
			tmp_return_item['price'] = item.get('price')
			tmp_return_item['product_url'] = item.get('product_url')
			tmp_return_item['image_url'] = item.get('image_url')
			tmp_return_item['simi'] = item.get('simi')
			tmp_return_item['source'] = item.get('source')
			#for TTK
			if tmp_return_item['source'] == 'gf':
				if tmp_return_item['simi'] == ttk_gf_simi:
					return_list.append(tmp_return_item)
			elif tmp_return_item['source'] == 'lf':
				if tmp_return_item['simi'] > ttk_lf_simi:
					return_list.append(tmp_return_item)
		if len(return_list) <= 0:
			log.info('for_tts return result none num %s' % len(return_list))
			return None
		#for item in return_list:
		#	print 'source %s' % item.get('source')
		#	print 'simi %s' % item.get('simi')
		#
		log.info('for_tts return result num %s' % len(return_list))
		return return_list
		
	else:
		log.error('status code error %s ' % r.status_code)
		return None
	
			
	
	
