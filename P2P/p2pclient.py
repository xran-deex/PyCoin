import socket, pickle, threading, socketserver
from P2P.messages import Message
from P2P.p2pserver import P2PServer
#from TransactionManager.transaction import Transaction
from struct import *

class P2PClient:
  HOST = '192.168.1.2'   # hard coded IP of the peer list server (for now)
  PORT = P2PServer.PORT  # grab the port number of the server
  CLIENT_PORT = 65000       # right now this is set prior to creating a P2PClient
  server = None
  
  def __init__(self, host):
    print('Creating client...')
    self.p2pserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Connecting to host...')
    self.p2pserver.connect((host, P2PClient.PORT))
    self.myIP = self.p2pserver.getsockname()[0] # the ip of this machine
    
  def send_message(self, message, payload=None):
    print('Sending message...')
    if message == Message.ADD:
      # if the message is add, send an 'ADD' message to the p2p server
      self.p2pserver.sendall(message + pack('I', P2PClient.CLIENT_PORT))
      self.peer_list = pickle.loads(self.p2pserver.recv(1024).strip())
      print('Received peer list: ', self.peer_list)
      
    elif message == Message.NEW_TRANSACTION:
      # if the message is 'NEW_TRANSACTION', send the message and payload (packed transaction) to each peer
      for peer in self.peer_list:
        
        # make sure we don't send the transaction back to ourselves.
        if peer[0] == self.myIP and peer[1] == P2PClient.CLIENT_PORT:
          continue
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Connecting to peer', peer)
        s.connect(peer)
        s.sendall(message)
        print('sending payload...')
        s.sendall(payload)
        s.close()
    
    elif message == Message.REMOVE:
      self.p2pserver.sendall(message)
  
  def broadcast_transaction(self, t):
    self.send_message(Message.NEW_TRANSACTION, t)
  
  def __del__(self):
    try:
      self.p2pserver.sendall(Message.QUIT)
    except:
      pass
    finally:
      self.p2pserver.close()
      if P2PClient.server:
        P2PClient.server.shutdown()
        print('server dying...')
      
  
  def start_server():
    print('starting server...')
    HOST = ''     #allow connections from any ip address
    print('Serving on: ', ('', P2PClient.CLIENT_PORT))
    P2PClient.server = socketserver.TCPServer((HOST, P2PClient.CLIENT_PORT), TCPHandler)
    print('running...')
    P2PClient.server.serve_forever()
  
  #def run():
  t = threading.Thread(target=start_server)
  t.start()

class TCPHandler(socketserver.BaseRequestHandler):
  """ Handles incoming tcp requests """
  def handle(self):
    print('received message from a peer...')
    message = self.request.recv(1024).strip()
    if message == Message.NEW_TRANSACTION:
      trans = self.request.recv(1024).strip()
      t = Transaction()
      t.unpack(trans)

if __name__ == '__main__':
  import sys
  from keystore import KeyStore
  port = sys.argv[1]
  P2PClient.CLIENT_PORT = int(port)
  trans = Transaction()
  trans.add_input(Transaction.Input(20, b'FFFFFFFF'))
  trans.add_output(Transaction.Output(10, KeyStore.getPublicKey())) # just pay to ourselves for now
  trans.add_input(Transaction.Input(5, b'FFFFFFFF'))
  s = trans.build_struct()
  
  c = P2PClient()
  c.send_message(Message.add)
  c.send_message(Message.NEW_TRANSACTION, s)
  
  import time
  time.sleep(5)
  
  trans = Transaction()
  trans.add_input(Transaction.Input(100, b'FFFFFFFF'))
  trans.add_output(Transaction.Output(55, KeyStore.getPublicKey())) # just pay to ourselves for now
  trans.add_input(Transaction.Input(4, b'FFFFFFFF'))
  s = trans.build_struct()
  c.send_message(Message.NEW_TRANSACTION, s)