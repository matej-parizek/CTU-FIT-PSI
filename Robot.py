import socket
import sys
from enum import Enum
from _thread import *
import threading
import time

"""MESSAGES"""
SERVER_CONFIRMATION=""
SERVER_MOVE= "102 MOVE\a\b".encode()
SERVER_TURN_LEFT="103 TURN LEFT\a\b".encode()
SERVER_TURN_RIGHT="104 TURN RIGHT\a\b".encode()
SERVER_PICK_UP="105 GET MESSAGE\a\b".encode()
SERVER_LOGOUT="106 LOGOUT\a\b".encode()
SERVER_KEY_REQUEST="107 KEY REQUEST\a\b".encode()
SERVER_OK="200 OK\a\b".encode()

SERVER_LOGIN_FAILED="300 LOGIN FAILED\a\b".encode()
SERVER_SYNTAX_ERROR="301 SYNTAX ERROR\a\b".encode()
SERVER_LOGIC_ERROR="302 LOGIC ERROR\a\b".encode()
SERVER_KEY_OUT_OF_RANGE_ERROR="303 KEY OUT OF RANGE\a\b".encode()

TIMEOUT= "TIMEOUT\a\b".encode()
class Direction(Enum):
    NORTH=0
    WEST=3
    SOUTH=2
    EAST=1


class Listener:
    def __init__(self,connection):
        self.connection=connection
        self.raw=''
        self.data=''
        self.buffer=[]
        self.name=False
        self.mess=False
        self.recharge=False
    def listening(self):
        self.connection.settimeout(1)
        if self.recharge==True:
            self.connection.settimeout(5)
        while True:
            timeout = time.time() + 1
            try:
                message=self.connection.recv(1024)
                if message:
                    data=message.decode('ascii')
                    self.raw+=data
                    return True
            except:
                break
        return None
    def corrUser(self,data):
        buffer=data.split('\a\b')
        return len(buffer[0])<=18
    def corrMess(self,data):
        buffer=data.split('\a\b')
        return len(buffer[0])<100


    def recvMessage(self):
        if(self.buffer!=[]):
            self.data=self.buffer.pop()
            return True
        while True:
            if self.raw:
                if self.name==False and self.corrUser(self.raw)==False:
                    return False
                if self.corrMess(self.raw)==False:
                    self.connection.sendall(SERVER_SYNTAX_ERROR)
                    self.connection.close()
                    return False
            self.data+=self.raw
            self.raw=''
            if self.data[-2:]=='\a\b':
                self.buffer=self.data.split('\a\b')
                self.buffer.reverse()
                if(self.buffer.count('')>0):
                    self.buffer.remove('')
                self.data=self.buffer.pop()
                return True
            else:
                if self.listening()==None:
                    return False

    #zmena pro key
    def intChangeKey(self):
        try:
            if(self.data.count(' ')>0):
                return self.data
            numbers=int(self.data)
            return numbers
        except:
            return self.data
    #zmena pro souradnice
    def intChange(self):
        try:
            if self.data.count(' ')>2:
                return self.data
            data=self.data.split(' ')
            x=int(data[1])
            y=int(data[2])
            return [x,y]
        except:
            return self.data
    def getName(self):
        rec=self.recvMessage()
        self.name=True
        if rec==True:
            data=self.data[:]
            self.data=''
            """NAME ERROR"""
            if (len(data)>18):
                self.connection.sendall(SERVER_SYNTAX_ERROR)
                self.connection.close()
                return None
            return data
        else:
            self.connection.sendall(SERVER_SYNTAX_ERROR)
            self.connection.close()
            return None
    def pickMess(self):
        rec = self.recvMessage()
        if rec == True:
            data = self.data[:]
            if data=="RECHARGING":
                self.connection.sendall(SERVER_LOGIC_ERROR)
                self.connection.close()
                return None
            if len(data)>100:
                self.connection.sendall(SERVER_SYNTAX_ERROR)
                self.connection.close()
                return None
            self.data = ''
            return data
        else:
            return None
    def getKey(self):
        if self.recvMessage():
            mess=self.intChangeKey()
            if type(mess)==str:
                if(mess=='RECHARGING'):
                    self.data=''
                    self.recharge=True
                    if (self.recvMessage()==False):
                        self.connection.close()
                        return False
                    if self.data =="FULL POWER":
                        self.recharge = False
                        self.data=''
                        if self.recvMessage():
                            mess=self.intChangeKey()
                            return mess
                        else:
                            self.connection.close()
                            return False
                    else:
                        self.connection.sendall(SERVER_LOGIC_ERROR)
                        self.connection.close()
                        return False
                self.connection.sendall(SERVER_SYNTAX_ERROR)
                self.connection.close()
                return False
            self.data=''
            return mess
        else:
            self.connection.close()
            return False

    def getMessage(self):
        if self.recvMessage():
            data=self.data.partition(' ')
            if data[0] == "OK":
                number=self.intChange()
                self.data=''
                if type(number)!=list:
                    self.connection.sendall(SERVER_SYNTAX_ERROR)
                    self.connection.close()
                    return None
                return number
            if data[0]=="RECHARGING":
                self.data = ''
                self.recharge = True
                if (self.recvMessage() == False):
                    self.connection.close()
                    return False
                if self.data == "FULL POWER":
                    self.recharge = False
                    self.data = ''
                    if self.recvMessage():
                        data = self.data.partition(' ')
                        if data[0] == "OK":
                            number = self.intChange()
                            self.data = ''
                            if type(number) != list:
                                self.connection.sendall(SERVER_SYNTAX_ERROR)
                                self.connection.close()
                                return None
                            return number
                    else:
                        self.connection.close()
                        return False
                else:
                    self.connection.sendall(SERVER_LOGIC_ERROR)
                    self.connection.close()
                    return False
        else:
            self.connection.sendall(SERVER_SYNTAX_ERROR)
            self.connection.close()


class Authentizator:
    def __init__(self,connerction,listening):
        self.connection=connerction
        self.listenig=listening
    def keyServer(self,id):
        if id == 0:
            return 23019
        if id == 1:
            return 32037
        if id == 2:
            return 18789
        if id == 3:
            return 16443
        if id == 4:
            return 18189
        return None
    def keyClient(self,id):
        if id == 0:
            return 32037
        if id == 1:
            return 29295
        if id == 2:
            return 13603
        if id == 3:
            return 29533
        if id == 4:
            return 21952
        return None
    def hashCode(self,name,serverKey):
        number=0
        for i in range(0,len(name)):
            number+=ord(name[i])
        return ((number * 1000) + serverKey) % 65536
    def hashCompare(self,name,serverKey,clientKey):
        number=0
        for i in range(0,len(name)):
            number+=ord(name[i])
        return ((number * 1000) + serverKey) % 65536 == clientKey
    def autention(self):
        """read Name"""
        name=self.listenig.getName()
        if(name==None):
            return False
        self.connection.sendall(SERVER_KEY_REQUEST)
        """recv key"""
        key=self.listenig.getKey()
        """read Server key"""

        if type(key) != int:
            return False
        keyServer=self.keyServer(key)
        if(keyServer and type(keyServer)==int):
            """Sending key"""
            self.connection.sendall((str(self.hashCode(name,keyServer))+'\a\b').encode())
        else:
            self.connection.sendall(SERVER_KEY_OUT_OF_RANGE_ERROR)
            self.connection.close()
            return False
        """read Client key"""

        keyClient=self.keyClient(key)
        keyClientRecv=self.listenig.getKey()
        if keyClientRecv==False:
            return False
        if keyClientRecv>99999:
            self.connection.sendall(SERVER_SYNTAX_ERROR)
            self.connection.close()
            return False

        if (keyClientRecv and keyClient):
            """Compare keys"""
            if self.hashCompare(name,keyClient,keyClientRecv):
                self.connection.sendall(SERVER_OK)
                return True
        else:
            self.connection.sendall(SERVER_KEY_OUT_OF_RANGE_ERROR)
            self.connection.close()
            return False
        self.connection.sendall(SERVER_LOGIN_FAILED)
        self.connection.close()
        return False

class Robot:
    def __init__(self,connection,listening):
        self.connection=connection
        self.listening=listening
        self.position=[99,99]
        self.direction=None
    def turnX(self):
        if(self.position[0]>0):
            if self.direction==Direction.SOUTH:
                self.direction=Direction.EAST
                self.connection.sendall(SERVER_TURN_RIGHT)
            elif self.direction==Direction.WEST:
                self.direction=Direction.SOUTH
                self.connection.sendall(SERVER_TURN_RIGHT)
            elif self.direction==Direction.NORTH:
                self.direction=Direction.EAST
                self.connection.sendall(SERVER_TURN_LEFT)
            elif self.direction==Direction.EAST:
                return True
        if self.position[0]<0:
            if self.direction==Direction.SOUTH:
                self.direction=Direction.WEST
                self.connection.sendall(SERVER_TURN_LEFT)
            elif self.direction==Direction.EAST:
                self.direction=Direction.SOUTH
                self.connection.sendall(SERVER_TURN_LEFT)
            elif self.direction==Direction.NORTH:
                self.direction=Direction.WEST
                self.connection.sendall(SERVER_TURN_RIGHT)
            elif self.direction==Direction.WEST:
                return True
        return False

    def turnY(self):
        if (self.position[1] > 0):
            if self.direction == Direction.SOUTH:
                return True
            elif self.direction == Direction.WEST:
                self.direction = Direction.SOUTH
                self.connection.sendall(SERVER_TURN_RIGHT)
            elif self.direction == Direction.NORTH:
                self.direction = Direction.EAST
                self.connection.sendall(SERVER_TURN_LEFT)
            elif self.direction == Direction.EAST:
                self.connection.sendall(SERVER_TURN_LEFT)
                self.direction=Direction.SOUTH
        if self.position[1] < 0:
            if self.direction == Direction.NORTH:
                return True
            elif self.direction == Direction.WEST:
                self.direction = Direction.NORTH
                self.connection.sendall(SERVER_TURN_LEFT)
            elif self.direction == Direction.SOUTH:
                self.direction = Direction.EAST
                self.connection.sendall(SERVER_TURN_RIGHT)
            elif self.direction == Direction.EAST:
                self.connection.sendall(SERVER_TURN_RIGHT)
                self.direction=Direction.NORTH
        return False

    def checkDir(self):

        self.connection.sendall(SERVER_MOVE)
        self.position=self.listening.getMessage()
        if(self.position==None):
            return None
        prevPosition=self.position

        self.connection.sendall(SERVER_MOVE)
        self.position=self.listening.getMessage()
        if (self.position == None):
            return None


        if prevPosition == self.position:
            self.connection.sendall(SERVER_TURN_LEFT)
            self.position = self.position = self.listening.getMessage()
            if (self.position == None):
                return None
            prevPosition=self.position
            self.connection.sendall(SERVER_MOVE)
            self.position = self.position = self.listening.getMessage()
            if (self.position == None):
                return None

        if (self.position[0] == prevPosition[0] and self.position[1] == prevPosition[1] + 1):
            return Direction(0)

        elif (self.position[0] == prevPosition[0] + 1 and self.position[1] == prevPosition[1]):
            return Direction(3)

        elif (self.position[0] == prevPosition[0] and self.position[1] == prevPosition[1] - 1):
            return Direction(2)

        elif (self.position[0] == prevPosition[0] - 1 and self.position[1] == prevPosition[1]):
            return Direction(1)
    def findX(self):
        while True:
            if self.position[0]==0:
                break
            if self.turnX():
                prevPos=self.position[:]
                self.connection.sendall(SERVER_MOVE)
                self.position=self.listening.getMessage()
                if self.position== prevPos:
                    self.obstacle("x")
                continue
            self.position=self.listening.getMessage()

    def findY(self):
        while True:
            if self.position[1]==0:
                break
            if self.turnY():
                prevPos = self.position[:]
                self.connection.sendall(SERVER_MOVE)
                self.position = self.listening.getMessage()
                if self.position == prevPos:
                    self.obstacle("y")
                continue
            self.position = self.listening.getMessage()

    def obstacle(self, stav):
        self.connection.sendall(SERVER_TURN_RIGHT)
        self.position=self.listening.getMessage()
        self.connection.sendall(SERVER_MOVE)
        self.position = self.listening.getMessage()
        self.connection.sendall(SERVER_TURN_LEFT)
        self.position = self.listening.getMessage()
        self.connection.sendall(SERVER_MOVE)
        self.position = self.listening.getMessage()
        if( stav=="x" and self.position[0]==0):
            return
        if (stav == "y" and self.position[1] == 0):
            return
        self.connection.sendall(SERVER_MOVE)
        self.position = self.listening.getMessage()
        self.connection.sendall(SERVER_TURN_LEFT)
        self.position = self.listening.getMessage()
        self.connection.sendall(SERVER_MOVE)
        self.position = self.listening.getMessage()
        self.connection.sendall(SERVER_TURN_RIGHT)
        self.position = self.listening.getMessage()

    def move(self,recurse):
        if recurse==False:
            self.direction=self.checkDir()
            if self.direction==None:
                return False
            self.findX()
            self.findY()

        if self.position==[0,0]:
            self.connection.sendall(SERVER_PICK_UP)
            if(self.listening.pickMess()==None):
                return False
            self.connection.sendall(SERVER_LOGOUT)
            self.connection.close()
            return True





class Runner:
    def __init__(self,connection):
        self.connection=connection
    def run(self):
        listening=Listener(self.connection)
        aut=Authentizator(self.connection,listening)
        if(aut.autention()==False):
            return
        rob=Robot(self.connection,listening)
        rob.move(False)

def run(con):
    runner = Runner(con)
    runner.run()



def main():
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        number=int(sys.argv[1])
    except:
        print("Nezadano cislo")
        return False

    sock.bind(('localhost',number))
    threads=[]
    sock.listen(3)
    while True:
        con,add=sock.accept()
        threading.Lock().acquire()
        start_new_thread(run,(con,))




main()
