# this project is Authored by mayank vaswani just for learning propose and demonstrating 
# working of request filteration systems (ReqFiS)




# library

from http.server import BaseHTTPRequestHandler as hand, HTTPServer as svr
import requests as rq
import urllib.parse
import json
import datetime as dt


# genral varriables pls ignore
content=''

endpoint='0.0.0.0:8000'  


def add(add_to_content):
	global content
	content= content + str(add_to_content)+'\n'

# main request handler as a simple class with builtin base inctance of baseHTTPhandler, 
#____don't touch____
class MiddleWare(hand):

	global content

	def do_GET(self):
		self.forward()
	def do_POST(self):
		self.forward()
	def do_PUT(self):
		self.forward()
	def do_DELETE(self):
		self.forward()
	def do_OPTIONS(self):
		self.forward()
	
	
	def check(self, request):
		with open('log.txt','a') as log:
			log.write(request+'\n\n-----------------\n')
		with open('blacklist.json','r') as f :
			blist= json.loads(f.read())
			for item in blist["List"]:
				if item in request:
					with open('log.txt','a') as log:
						log.write(f'info:backlisted content found __({item})__\n\n----------------------\n\n')
					
					raise ValueError(f'backlisted content found __({item})__')
					request= f"this request was dropped because: {item}\n\n"+ request
					pass
			f.close()

	
	
	#forwards message to endpoint server as a proxy server
	
	
	def forward(self):
		
		global content
		all_header = self.headers
		chunk = self.rfile.read(int(self.headers.get('Content-Length',0)))
		rq_type= self.command
		address= f'http://{endpoint}{self.path}'
		client= self.client_address
		
		add(rq_type)
		add(address)
		add(all_header)
		add(chunk)
		add(client)
		add(dt.datetime.now())
		
		try:
			self.check(content)
			content=''
	
			if "Content-Length" in all_header:
				res=rq.request(url=address,method=rq_type,data=chunk)
				self.wfile.write(res.text.encode('utf-8'))
		
			else:
				res=rq.request(url=address,method=rq_type)
				self.wfile.write(res.text.encode('utf-8'))
		except ValueError :self.wfile.write(b'invaild or blacklisted element in request, hereby droped\n\n----------------\n')
			
			
#main code to run 
if __name__ == "__main__":
	try:
		main=svr(('127.0.0.1',80),MiddleWare)
		main.serve_forever()
		print("active on 127.0.0.1:80")
		main.server_close()
	#just in case execption
	except:
		print("error")
