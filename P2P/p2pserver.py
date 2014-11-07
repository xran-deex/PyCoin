import socket, threading, pickle
#from TransactionManager.transaction import *
from P2P.messages import Message
from struct import *

class P2PServer:
  
  HOST = ''                 # Symbolic name meaning all available interfaces
  PORT = 50007              # Arbitrary non-privileged port
  
  def __init__(self):
    self.peer_list = []
    print('Starting server...')
    self.start_server()
    
  def start_server(self):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.bind((P2PServer.HOST, P2PServer.PORT))
    self.socket.listen(2)
    print('Listening...')
    conn, addr = self.socket.accept()
    print('Connected by', addr)
    try:
      while 1:
          t = threading.Thread(target=self.handle_message, args=(addr, conn))
          t.start()
          print('waiting...')
          conn, addr = self.socket.accept()
    except:
      print('Good bye...')
    finally:
      conn.close()
      self.socket.close()
  
  def add_peer(self, peer, port):
    self.peer_list.append((peer, port))
    
  def remove_peer(self, peer, conn):
    toBeRemoved = None
    for p in self.peer_list:
      print(peer, p)
      if peer[0] == p[0]:
        toBeRemoved = p
        break
    if not toBeRemoved:
      return
    print('Removing peer: ', p)
    self.peer_list.remove(toBeRemoved)
    print('Peer list: ', self.peer_list)
    self.deliver_peer_list(conn)
    
  def deliver_peer_list(self, conn):
    conn.sendall(pickle.dumps(list(self.peer_list)))
  
  def handle_message(self, peer, conn):
    message = conn.recv(1024).strip()
    print('Received message', message)
    while message and message[:4] != Message.QUIT:
      
      if message[:3] == Message.ADD:
        print(peer)
        self.add_peer(peer[0], unpack('I', message[3:])[0])
        self.deliver_peer_list(conn)
        
      elif message[:15] == Message.NEW_TRANSACTION:
        port = message[15:]
        payload = conn.recv(1024).strip()
        self.send_to_peers(payload, port)
        
      elif message[:6] == Message.REMOVE:
        self.remove_peer(peer, conn)
        
      message = conn.recv(1024).strip()
      print('Received message', message)
    conn.close()
    print('thread dying...')
          
          
  def send_to_peers(self, payload, origin):
    ''' broadcast a message to all peers '''
    for peer, port in self.peer_list:
      #if port == origin:
       # continue
      print(peer)
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.connect(('localhost', port))
      print('sending payload...')
      s.sendall(payload)
        

if __name__ == "__main__":
    P2PServer()
