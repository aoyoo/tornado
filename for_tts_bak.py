# -*- coding=utf-8 -*-
import requests
import time
import json
import sys
reload(sys)
sys.setdefaultencoding('utf8')

#url = 'http://10.0.0.239:6012'
url = 'http://10.0.0.155:6011'

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


#return None if error
#else return result list
def postTTS(log, cid, image_data):

	head = {
			'classId': '70020',
			'b2c_flag': '2',
			'color':'0',
			'gf': '2',
			'lf': '2',
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
			'maxProPerGroup':'2',
	
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
		raw_list = r.text.split('\n')
		feat_list = []
		source_list = []
		group_num_list = []
		source = ['cf', 'gf', 'lf', 'tv']
		source_count = 0
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
			item['title'] = get_value_from_string(feat_list[i],'productTitle')
			item['product_url'] = get_value_from_string(feat_list[i],'url')
			item['simi'] = get_value_from_string(feat_list[i],'similarity')
			item['image_url'] = get_value_from_string(feat_list[i],'mainViewImagePath')
			item['price'] = get_value_from_string(feat_list[i],'price')[:-2]
			item['sales'] = get_value_from_string(feat_list[i],'salesVolume')
			item['source'] = source_list[i]
			result_list.append(item)

		#for feat in feat_list:
		#	#print feat
		#	#print 'rank_score',get_value_from_string(feat,'rank_score')
		#	item = {}
		#	pid = get_value_from_string(feat,'id')
		#	item['pid'] = pid
		#	item['title'] = get_value_from_string(feat,'productTitle')
		#	item['product_url'] = get_value_from_string(feat,'url')
		#	item['simi'] = get_value_from_string(feat,'similarity')
		#	item['image_url'] = get_value_from_string(feat,'mainViewImagePath')
		#	item['price'] = get_value_from_string(feat,'price')[:-2]
		#	item['sales'] = get_value_from_string(feat,'salesVolume')
		#	result_list.append(item)
	
		log.debug('TTS result list len: %s' % len(result_list))
	

		if len(result_list) == 0:
			return "{'status':1}"

		#print result_list

		resNum = len(result_list)

		returnResultBegin = "{'status':0,'content':["
		returnResult = "{'status':0,'content':["
		returnResultEnd = "]}"
		resultResultItem = "{'title':'%s', 'price':'%s', 'product_url':'%s', 'image_url':'%s', 'simi':'%s', 'source':'%s'}"
		for i in range(0, resNum-1):
			returnResult += resultResultItem % (
						result_list[i].get('title'), 
						result_list[i].get('price'), 
						result_list[i].get('product_url'), 
						result_list[i].get('image_url'),
						result_list[i].get('simi'),
						result_list[i].get('source')
					)
			returnResult += ','

		returnResult += resultResultItem % (
					result_list[resNum-1].get('title'), 
					result_list[resNum-1].get('price'), 
					result_list[resNum-1].get('product_url'), 
					result_list[resNum-1].get('image_url'),
					result_list[resNum-1].get('simi'),
					result_list[resNum-1].get('source')
				)

		returnResult += returnResultEnd
		log.info('for_tts result num %s' % resNum)
		#print returnResult
		return returnResult

	else:
		log.error('status code error %s ' % r.status_code)
		return "{'status':1}"



