import pyjsonrpc
import serial
import time

class SerialComs(object):

    def __init__(self):
        ser = serial.Serial('/dev/ttyMFD1', baudrate=115200, timeout = 0.1) #Define serial port
        self.ser = ser          #Store serial port in class self
        if not ser.isOpen():
            ser.open()              #Open

    def echo(self,a):
        return 'Serial Coms '+str(a)
        
    def openRoomba(self):
        ser = self.ser
        success = ser.write(chr(128))       #Roomba to serial mode
        time.sleep(0.1)
        success = ser.write(chr(131))       #Roomba to safe mode
        time.sleep(0.1)
        return 1

    def roombaClean(self):
        ser = self.ser
        success = ser.write(chr(135))  #Roomba clean.
        return 1

    def roombaSafe(self):
        ser = self.ser
        success = ser.write(chr(130)) #Roomba to safe mode.
        time.sleep(0.1)
        return 1
    
    def roombaLeft(self):
        ser = self.ser
        success = ser.write(chr(137)+chr(0)+chr(200)+chr(1)+chr(244)) #Motors, speed 200, radius 500
        return 1
    
    def roombaRight(self):
        ser = self.ser
        success = ser.write(chr(137)+chr(0)+chr(200)+chr(254)+chr(12)) #Motors, speed 200, radius -500
        return 1

    def roombaStraight(self):
        ser = self.ser
        success = ser.write(chr(137)+chr(0)+chr(200)+chr(0)+chr(0))  #Motors, speed 200, radius 0
        return 1

    def roombaStop(self):
        ser = self.ser
        success = ser.write(chr(137)+chr(0)+chr(1)+chr(0xff)+chr(0xff))  #Motors, speed 0, special case 1 for turn counterclockwise

    def closeRoomba(self):
        ser = self.ser
        ser.close()
        return 1

class RequestHandler(pyjsonrpc.HttpRequestHandler):

    @pyjsonrpc.rpcmethod
    def echo(self, a):
        return 'Server '+str(a)

    @pyjsonrpc.rpcmethod
    def comsEcho(self, a):
        foo = coms.echo(a)
        return foo

    @pyjsonrpc.rpcmethod
    def initBot(self):
        status = coms.openRoomba()
        return 'Hi!'

    @pyjsonrpc.rpcmethod
    def clean(self):
        status=coms.roombaClean()
        return 'clean'

    @pyjsonrpc.rpcmethod
    def safe(self):
        status = coms.roombaSafe()
        return 'safe'
        
    @pyjsonrpc.rpcmethod
    def left(self):
        status = coms.roombaLeft()
        return 'left'

    @pyjsonrpc.rpcmethod
    def right(self):
        status = coms.roombaRight()
        return 'right'

    @pyjsonrpc.rpcmethod
    def straight(self):
        status = coms.roombaStraight()
        return 'straight'

    @pyjsonrpc.rpcmethod
    def stop(self):
        status = coms.roombaStop()
        return 'Weeeeee!!!!!'

    @pyjsonrpc.rpcmethod
    def closeBot(self):
        status = coms.closeRoomba()
        return 'Bye!'
    
coms = SerialComs()
http_server = pyjsonrpc.ThreadingHttpServer(server_address = ('0.0.0.0',8081), RequestHandlerClass = RequestHandler)
print "Starting http server..."
print "URL : http://localhost:8081"
http_server.serve_forever()
