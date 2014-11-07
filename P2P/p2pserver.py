import socket, threading, pickle
from TransactionManager.transaction import *
from P2P.messages import Message
from struct import *

class P2PServer:
  
  HOST = ''                 # Symbolic name meaning all available interfaces
  PORT = 50007              # Arbitrary non-privileged port
  
  def __init__(self):
    self.peer_list = {}
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
  
  def add_peer(self, peer, val):
    self.peer_list[peer] = val
    
  def deliver_peer_list(self, peer):
    pass
  
  def handle_message(self, peer, conn):
    message = conn.recv(1024).strip()
    while message != b'':
      
      print('Received message', message)
      if message[:3] == Message.add:
        print(peer)
        self.add_peer(peer[1], unpack('I', message[3:])[0])
        
        conn.sendall(pickle.dumps(list(self.peer_list.keys())))
      elif message[:15] == Message.new_transaction:
        port = message[15:]
        payload = conn.recv(1024).strip()
        self.send_to_peers(payload, port)
        
      message = conn.recv(1024).strip()
          
  def send_to_peers(self, payload, origin):
    for peer, port in self.peer_list.items():
      if port == origin:
        continue
      print(peer)
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.connect(('localhost', port))
      print('sending payload...')
      s.sendall(payload)
        

if __name__ == "__main__":
    P2PServer()