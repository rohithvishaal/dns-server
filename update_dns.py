import requests
from subprocess import PIPE
import subprocess
from time import sleep
import os 
check_delay = 5

def out(command):
    result = subprocess.run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell= True)
    return result.stdout

def replace_text(source, target):
    # creating a variable and storing the text
    # that we want to search
    search_text = source
    print("Search text", source)
    # creating a variable and storing the text
    # that we want to add
    replace_text = target
    print("target text", target) 
    # Opening our text file in read only
    # mode using the open() function
    with open(r'/etc/hosts', 'r') as file:
      
        # Reading the content of the file
        # using the read() function and storing
        # them in a new variable
        data = file.read()
      
        # Searching and replacing the text
        # using the replace() function
        data = data.replace(search_text, replace_text)
      
    # Opening our text file in write only
    # mode to write the replaced content
    with open(r'/etc/hosts', 'w') as file:
      
        # Writing the replaced data in our
        # text file
        file.write(data)
      
    # Printing Text replaced
    print("Text replaced")

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        host_site_ip = out("cat /etc/hosts | tail -n 1 | cut -d ' ' -f 1")
        self.wfile.write("{}".format(host_site_ip).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))
        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))
        new_ip = post_data.decode('utf-8').split("=")[1]
        host_ip = out('cat /etc/hosts | grep site.com | cut -d " " -f 1')
        #os.system("sudo sed -i 's/10.0.2.7/10.0.2.5/gI' /etc/hosts")
        f = open("/etc/hosts", "r")
        data = f.readlines()
        trimmed_data = data[:-1]
        f.close()
        f = open("/etc/hosts", "w")
        w_data = f"{new_ip} site.com"
        f.writelines(trimmed_data)
        f.write(w_data)
        f.close()
        mod_ip = out('cat /etc/hosts | grep site.com | cut -d " " -f 1')
        print(f"previous_ip:{host_ip} current_ip:{mod_ip}")
        print("Changes made! restarting dnsmasq")
        out("sudo systemctl restart dnsmasq")
        

def run(server_class=HTTPServer, handler_class=S, port=80):
    logging.basicConfig(level=logging.INFO)
    server_address = ('10.0.2.4', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
