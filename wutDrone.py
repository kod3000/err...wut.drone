
#!/usr/bin/python3

import numpy
import sys
import cv2
import time
import json
from djitellopy import tello
import threading
from time import sleep
from PIL import Image
from io import BytesIO
import urllib.parse
import subprocess as sp
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

drun= tello.Tello()
drun.connect()
drun.streamon()


StartTime=time.time()

breath = 0
def foo():
    global drun
    global breath
    wht = drun.get_battery()
    breath = breath + 1
    if wht < 91 and breath > 10:
        print("change out battery " + str(wht))
        breath = 0



class ThreadJob(threading.Thread):
    def __init__(self,callback,event,interval):
        """ Something Profound

        """
        '''runs the callback function after interval seconds

        :param callback:  callback function to invoke
        :param event: external event for controlling the update operation
        :param interval: time in seconds after which are required to fire the callback
        :type callback: function
        :type interval: int
        '''
        self.callback = callback
        self.event = event
        self.interval = interval
        super(ThreadJob,self).__init__()

    def run(self):
        while not self.event.wait(self.interval):
            self.callback()



event = threading.Event()

k = ThreadJob(foo,event,2)
k.start()
print ('''

    Welcome to Drone Testing
    Here we want the following to happen :
    - make a api list command that viewable from browser
    - create module that controls the drone
    - fix camera to be good quality

    ''')

class CamHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        global regularImage,locationServer, drun

        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            while True:
                try:
                    # here we want to put up a black frame loading in our camera image
                    imgRGB = cv2.cvtColor(drun.get_frame_read().frame,cv2.COLOR_BGR2RGB)
                    jpg = Image.fromarray(imgRGB)
                    tmpFile = BytesIO()
                    jpg.save(tmpFile,'JPEG')
                    self.wfile.write("--jpgboundary".encode())
                    self.send_header('Content-type','image/jpeg')
                    self.send_header('Content-length',str(tmpFile.getbuffer().nbytes))
                    self.end_headers()
                    jpg.save(self.wfile,'JPEG')
                    time.sleep(0.05)
                except KeyboardInterrupt:
                    break
            return
        if self.path.endswith('ok.html'):
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write('<html><head></head><body>'.encode())
            self.wfile.write(('<img src="http://10.0.0.87:8087/cam.mjpg"/>').encode())
            self.wfile.write('</body></html>'.encode())
            return
        if self.path.endswith('index.html'):
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write('<html><head></head><body>'.encode())
            
            self.wfile.write('</body></html>'.encode())
            return
        if self.path.endswith('api/battery'):
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            
            your_json = '["foo", {"battery":'+str(drun.get_battery())+',  "temp":'+str(drun.get_temperature())+' , "sdk":'+str(drun.query_sdk_version())+' , "serial":'+str(drun.query_serial_number())+' }]'
            parsed = json.loads(your_json)
            self.wfile.write((json.dumps(parsed, indent=4, sort_keys=True)).encode())
            return
        if self.path.endswith('api/freeze'):
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            your_json = '["ok"]'
            parsed = json.loads(your_json)
            self.wfile.write((json.dumps(parsed, indent=4, sort_keys=True)).encode())
            return
        if self.path.endswith('api/foward'):
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            drun.move_forward(100)
            your_json = '["ok"]'
            parsed = json.loads(your_json)
            self.wfile.write((json.dumps(parsed, indent=4, sort_keys=True)).encode())
            return
        if self.path.endswith('api/back'):
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            drun.move_back(100)
            your_json = '["ok"]'
            parsed = json.loads(your_json)
            self.wfile.write((json.dumps(parsed, indent=4, sort_keys=True)).encode())
            return
        if self.path.endswith('api/up'):
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            drun.move_up(50)
            your_json = '["ok"]'
            parsed = json.loads(your_json)
            self.wfile.write((json.dumps(parsed, indent=4, sort_keys=True)).encode())
            return
        if self.path.endswith('api/down'):
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            drun.move_down(100)
            your_json = '["ok"]'
            parsed = json.loads(your_json)
            self.wfile.write((json.dumps(parsed, indent=4, sort_keys=True)).encode())
            return
        if self.path.endswith('api/left'):
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            drun.move_left(100)
            your_json = '["ok"]'
            parsed = json.loads(your_json)
            self.wfile.write((json.dumps(parsed, indent=4, sort_keys=True)).encode())
            return
        if self.path.endswith('api/right'):
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            drun.move_right(100)
            your_json = '["ok"]'
            parsed = json.loads(your_json)
            self.wfile.write((json.dumps(parsed, indent=4, sort_keys=True)).encode())
            return
        if self.path.find('api/rotate') != -1:
            o = urllib.parse.urlparse(self.path)
            print(str(urllib.parse.parse_qs(o.query)))
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            drun.rotate_clockwise(20)
            your_json = '["ok"]'
            parsed = json.loads(your_json)
            self.wfile.write((json.dumps(parsed, indent=4, sort_keys=True)).encode())
            return
        if self.path.endswith('api/takeoff'):
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            drun.takeoff()
            your_json = '["ok"]'
            parsed = json.loads(your_json)
            self.wfile.write((json.dumps(parsed, indent=4, sort_keys=True)).encode())
            return
        if self.path.endswith('api/land'):
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            drun.land()
            your_json = '["ok"]'
            parsed = json.loads(your_json)
            self.wfile.write((json.dumps(parsed, indent=4, sort_keys=True)).encode())
            return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def main():
    locationServer = '10.0.0.87'
    try:
        server = ThreadedHTTPServer((locationServer, 8087), CamHandler)
        print( "server started")
        server.serve_forever()
    except KeyboardInterrupt:
        #capture.release()
        server.socket.close()

if __name__ == '__main__':
    main()

