#from PyCoin.TransactionManager.transaction import Transaction

import socket, pickle, threading, socketserver
from P2P.messages import Message
from TransactionManager.transaction import Transaction
from struct import *

class P2PClient:
  HOST = 'localhost'
  PORT = 50007
  SERVER_PORT = 50008
  
  def __init__(self):
    print('Creating client...')
    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Connecting to host...')
    self.s.connect((P2PClient.HOST, P2PClient.PORT))
    
  def send_message(self, message, payload=None):
    print('Sending message...')
    self.s.sendall(message + pack('I', P2PClient.SERVER_PORT))
    if message == Message.add:
      self.peer_list = pickle.loads(self.s.recv(1024).strip())
      print('Received peer list: ', self.peer_list)
    elif message == Message.new_transaction:
      print('sending payload...')
      self.s.sendall(payload)
  
  def __del__(self):
    self.s.sendall(b'quit')
    self.s.close()
  
  def start_server():
    print('starting server...')
    HOST = "localhost"

    server = socketserver.TCPServer((HOST, P2PClient.SERVER_PORT), TCPHandler)
    server.serve_forever()
  
  t = threading.Thread(target=start_server)
  t.start()

class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
      print('received transaction...')
      message = self.request.recv(1024).strip()
      t = Transaction()
      t.unpack(message)

if __name__ == '__main__':
  import sys
  from keystore import KeyStore
  port = sys.argv[1]
  P2PClient.SERVER_PORT = int(port)
  trans = Transaction()
  trans.add_input(Transaction.Input(20, b'FFFFFFFF'))
  trans.add_output(Transaction.Output(10, KeyStore.getPublicKey())) # just pay to ourselves for now
  trans.add_input(Transaction.Input(5, b'FFFFFFFF'))
  s = trans.build_struct()
  
  c = P2PClient()
  c.send_message(Message.add)
  c.send_message(Message.new_transaction, s)
  
  import time
  time.sleep(5)
  
  trans = Transaction()
  trans.add_input(Transaction.Input(100, b'FFFFFFFF'))
  trans.add_output(Transaction.Output(55, KeyStore.getPublicKey())) # just pay to ourselves for now
  trans.add_input(Transaction.Input(4, b'FFFFFFFF'))
  s = trans.build_struct()
  c.send_message(Message.new_transaction, s)