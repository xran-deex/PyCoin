import socket, threading, pickle, signal
from P2P.messages import Message
from struct import *

class P2PServer:
  
  HOST = ''                 # Symbolic name meaning all available interfaces
  PORT = 50007              # Arbitrary non-privileged port
  DEBUG = False
  
  def __init__(self):
    self.peer_list = []
    print('Starting server...')
    self.t = threading.Thread(target=self.start_server)
    self.t.start()
    signal.signal( signal.SIGINT, self.signal_handler) #register for keyboard interrupt signal
    
  def signal_handler(self, signal, frame):
    ''' Gracefully handle shudown by listening for ctrl + c '''
    self.shutdown_server()
    
  def start_server(self):
    self.run_server = True
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.bind((P2PServer.HOST, P2PServer.PORT))
    self.socket.listen(0)
    print('Listening...')
    conn, addr = self.socket.accept()
    print('Connected by', addr)
    try:
      while self.run_server:
          t = threading.Thread(target=self.handle_message, args=(addr, conn))
          t.start()
          print('waiting...')
          conn, addr = self.socket.accept()
          print('Connected by', addr)
    except:
      print('Good bye...')
    finally:
      print('Good bye...')
      conn.close()
      self.socket.close()
      
  def shutdown_server(self):
    self.run_server = False
    # Artificially connect to the waiting socket, just to close the loop
    s = socket.socket(socket.AF_INET,
                  socket.SOCK_STREAM)
    s.connect( (P2PServer.HOST, P2PServer.PORT))
    self.socket.close()
    s.close()
    print('server dead')
  
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
    if len(self.peer_list) == 0 and P2PServer.DEBUG:
      self.shutdown_server()
    #else:
      #self.deliver_peer_list(conn)
    
  def deliver_peer_list(self, conn):
    conn.sendall(pickle.dumps(list(self.peer_list)))
  
  def handle_message(self, peer, conn):
    message = conn.recv(1024).strip()
    print('Received message', message)
    try:
      while message and message != Message.QUIT:
        
        if message == Message.ADD:
          print(peer)
          port = conn.recv(1024).strip()
          port = unpack('I', port)[0]
          self.add_peer(peer[0], port)
          self.deliver_peer_list(conn)
          self.send_to_peers(pickle.dumps(list(self.peer_list)), port, Message.ADD)
          
        # elif message == Message.NEW_TRANSACTION:
        #   port = message[15:]
        #   payload = conn.recv(1024).strip()
        #   self.send_to_peers(payload, port)
          
        elif message[:6] == Message.REMOVE:
          self.remove_peer(peer, conn)
          
        message = conn.recv(1024).strip()
        print('Received message', message)
    except (KeyboardInterrupt):
      print('Caught keyboard interrupt.')
    self.remove_peer(peer, conn)
    conn.close()
          
          
  def send_to_peers(self, payload, origin, message):
    ''' broadcast a message to all peers '''
    print(self.peer_list)
    for peer, port in self.peer_list:
      if port == origin:
        continue
      print(peer)
      try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((peer, port))
        
        if message:
          print('sending message...')
          s.sendall(message)
          import time
          time.sleep(0.1)
        print('sending payload...')
        s.sendall(payload)
      except:
        print('Connection failed')
        

if __name__ == "__main__":
    P2PServer()
