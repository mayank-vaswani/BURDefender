# this project is Authored by Mayank Vaswani
# working of request Filtering Systems (ReqFiS)


# library

from http.server import BaseHTTPRequestHandler as hand, HTTPServer as svr
import requests as rq
import json
import datetime as dt
import tkinter


# genral varriables pls ignore
content = ''
endpoint = '0.0.0.0:8000'


def add(add_to_content):
    global content
    content = content + str(add_to_content) + '\n'

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
        with open('log.txt', 'a') as log:
            log.write(request + '\n\n-----------------\n')
        try:
            with open('blacklist.json', 'r') as f:
                blist = json.loads(f.read())
                for item in blist["List"]:
                    if item in request:
                        with open('log.txt', 'a') as log:
                            log.write(f'info:backlisted content found __({item})__\n\n----------------------\n\n')

                        raise ValueError(f'backlisted content found __({item})__')
        except FileNotFoundError:
            with open('log.txt', 'a') as log:
                log.write('Warning: blacklist.json not found. Skipping blacklist check.\n\n-----------------\n')
        except json.JSONDecodeError:
            with open('log.txt', 'a') as log:
                log.write('Error: Could not decode blacklist.json. Skipping blacklist check.\n\n-----------------\n')


    #forwards message to endpoint server as a proxy server


    def forward(self):

        global content
        all_header = self.headers
        content_length = int(self.headers.get('Content-Length', 0))
        chunk = self.rfile.read(content_length)
        rq_type = self.command
        address = f'http://{endpoint}{self.path}'
        client = self.client_address

        add(f"Request Type: {rq_type}")
        add(f"Address: {address}")
        add(f"Headers:\n{all_header}")
        add(f"Body:\n{chunk.decode('utf-8', errors='ignore')}")
        add(f"Client Address: {client}")
        add(f"Timestamp: {dt.datetime.now()}")

        try:
            self.check(content)
            content = ''

            try:
                if "Content-Length" in all_header:
                    res = rq.request(url=address, method=rq_type, data=chunk, headers=dict(all_header))
                    self.send_response(res.status_code)
                    for key, value in res.headers.items():
                        self.send_header(key, value)
                    self.end_headers()
                    self.wfile.write(res.content)
                else:
                    res = rq.request(url=address, method=rq_type, headers=dict(all_header))
                    self.send_response(res.status_code)
                    for key, value in res.headers.items():
                        self.send_header(key, value)
                    self.end_headers()
                    self.wfile.write(res.content)
            except rq.exceptions.RequestException as e:
                self.send_response(502)  # Bad Gateway
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f"<html><body><h1>Bad Gateway</h1><p>Error connecting to endpoint: {e}</p></body></html>".encode('utf-8'))

        except ValueError as e:
            self.send_response(400)  # Bad Request
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"<html><body><h1>Bad Request</h1><p>{e}</p></body></html>".encode('utf-8'))


def startSever() :
        global tk
        global endpoint_entry
        global endpoint
        new_endpoint = endpoint_entry.get()
        if new_endpoint:
            endpoint = new_endpoint
            print(f"Endpoint updated to: {endpoint}")
        tk.destroy()
        main = svr(('127.0.0.1', 80), MiddleWare)
        print("active on http://127.0.0.1:80")
        try:
            main.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            main.server_close()
            print('Server closed')

# Function to update the endpoint
def update_endpoint():
    global endpoint
    global endpoint_entry
    new_endpoint = endpoint_entry.get()
    if new_endpoint:
        endpoint = new_endpoint
        print(f"Endpoint updated to: {endpoint}")
        endpoint_entry.delete(0, tkinter.END) # Clear the entry field


#main code to run
if __name__ == "__main__":
    tk = tkinter.Tk()
    tk.title("BURdefender")
    tk.geometry('400x250')

    mainlabel = tkinter.Label(tk, text="BURdefender", font=("Arial", 24))
    mainlabel.pack(pady=20)

    changeEndpointframe = tkinter.Frame(tk)
    changeEndpointframe.pack(pady=10)

    changeEndpointlabel = tkinter.Label(changeEndpointframe, text="Target Endpoint:")
    changeEndpointlabel.pack()

    endpoint_entry = tkinter.Entry(changeEndpointframe, width=30)
    endpoint_entry.insert(0, endpoint)  # Set initial endpoint value
    endpoint_entry.pack()

    changeEndpointButton = tkinter.Button(changeEndpointframe, text="Update Endpoint", command=update_endpoint)
    changeEndpointButton.pack()

    startbutton = tkinter.Button(tk, text="Start Server on http://127.0.0.1:80", command=startSever, font=("Arial", 12), bg="lightblue")
    startbutton.pack(pady=20)

    tk.mainloop()
