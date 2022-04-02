import requests
from subprocess import PIPE
import subprocess
from time import sleep

def out(command):
	result = subprocess.run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
	return result.stdout

def get_ip():
	return out("ifconfig | head -n 2 | tail -n 1 | awk '{print $2}'").strip()

def get_nginx_ip():
    return out('cat /etc/nginx/sites-available/mytest.conf  | grep listen | cut -d " " -f 2 | cut -d ":" -f 1').strip()

current_ip = get_ip()
nginx_ip = get_nginx_ip()
print(f"current_ip:{current_ip}, nginx_ip:{nginx_ip}")
check_delay = 5
while True:
	sleep(check_delay)
	current_ip = get_ip()
	nginx_ip = get_nginx_ip()
	print("No change", flush=True, end="\r")
	if current_ip!= nginx_ip:
		print("IP change detected updating ip to DNS")
		print(f"current_ip:{current_ip} nginx_ip:{nginx_ip}")
		url = 'http://10.0.2.4:80'
		data = {'changed_ip': current_ip}
		try:
			r = requests.post(url=url , data=data)
			f = open("/etc/nginx/sites-available/mytest.conf", "r")
			print("updating ip in nginx mytest.conf")
			out(f"sudo sed -i 's/{nginx_ip}/{current_ip}/gI' /etc/nginx/sites-available/mytest.conf")
			print("IP changed in nginx")
			print(get_nginx_ip() == get_ip())
		except:
			print("error in post request")
			#out(f"sudo sed -i 's/{dom_ip}/{current_ip}/gI' /etc/hosts"
			# f = open("/etc/nginx/sites-available/mytest.conf", "w")
			# w_data = f"{current_ip}"
		finally:
			print("restarting nginx")
			out("sudo pkill nginx")
			out("sudo nginx")
