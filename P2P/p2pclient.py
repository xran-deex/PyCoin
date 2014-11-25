import socket, pickle, threading, socketserver
from P2P.messages import Message
from P2P.p2pserver import P2PServer

import logging
from globals import LOG_LEVEL

log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)

from struct import *
import time

class P2PClient(object):
  HOST = '192.168.1.2'   # hard coded IP of the peer list server (for now)
  PORT = P2PServer.PORT  # grab the port number of the server
  #CLIENT_PORT = 65000       # right now this is set prior to creating a P2PClient
  server = None
  
  def __init__(self, host, port=None):
    if port:
      P2PClient.CLIENT_PORT = port
    else:
      P2PClient.CLIENT_PORT = 65000
    log.info('Creating client on port... %d', self.CLIENT_PORT)
    self.p2pserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    log.info('Connecting to host...')
    self.p2pserver.connect((host, P2PClient.PORT))
    self.myIP = self.p2pserver.getsockname()[0] # the ip of this machine
    self.trans_queue = []
    self.received_trans = []
    self.received_blocks = []
    self.peer_list = []
    self.trans_listeners = []
    self.block_listeners = []
    
  def send_message(self, message, payload=None):
    log.info('Sending message...')
    import time
    if message == Message.ADD:
      # if the message is add, send an 'ADD' message to the p2p server
      self.p2pserver.sendall(message)
      
      time.sleep(0.1)
      self.p2pserver.sendall(pack('I', self.CLIENT_PORT))
      self.peer_list = pickle.loads(self.p2pserver.recv(1024).strip())
      
    elif message == Message.NEW_TRANSACTION:
      # if the message is 'NEW_TRANSACTION', send the message and payload (packed transaction) to each peer
      if len(self.peer_list) == 1 and self.peer_is_self(self.peer_list[0]):
        self.queue_transaction(payload)
        log.info('queued transaction')
        return
      for peer in self.peer_list:
        
        # make sure we don't send the transaction back to ourselves.
        if self.peer_is_self(peer):
          continue
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log.info('Connecting to peer %s', peer)
        s.connect(peer)
        log.info('sent message: %s', message)
        s.sendall(message)
        time.sleep(0.1)
        log.info('sending payload...')
        s.sendall(payload)
        s.close()
        
    elif message == Message.NEW_BLOCK:
      # handle a new block
      for peer in self.peer_list:
        
        if self.peer_is_self(peer):
          continue
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log.info('Connecting to peer %s', peer)
        s.connect(peer)
        log.info('sent message: %s', message)
        s.sendall(message)
        time.sleep(0.1)
        log.info('sending payload...')
        s.sendall(payload)
        s.close()
        
    
    elif message == Message.REMOVE:
      self.p2pserver.sendall(message)
      
  def peer_is_self(self, peer):
    return peer[0] == self.myIP and peer[1] == self.CLIENT_PORT
    
  def queue_transaction(self, t):
    self.trans_queue.append(t)
    
  def queue_item_received(self, message_type, t):
    if message_type == Message.NEW_TRANSACTION:
      self.received_trans.append(t)
    elif message_type == Message.NEW_BLOCK:
      self.received_blocks.append(t)
    
  def get_queued_transactions(self):
    return self.received_trans
    
  def subscribe(self, message_type, callback):
    """ Add listeners to get notified when new transactions are received from the network
    
    Param: listener
    """
    if message_type == Message.NEW_TRANSACTION:
      self.trans_listeners.append(callback)
    elif message_type == Message.NEW_BLOCK:
      self.block_listeners.append(callback)
      log.info('miner subscribed')
    
  def notify_subscribers(self, message_type, trans):
    if message_type == Message.NEW_TRANSACTION:
      for callback in self.trans_listeners:
        callback(trans)
    elif message_type == Message.NEW_BLOCK:
      for callback in self.block_listeners:
        callback(trans)
  
  def broadcast_transaction(self, t):
    self.notify_subscribers(Message.NEW_TRANSACTION, t)
    self.send_message(Message.NEW_TRANSACTION, t)
    
  def broadcast_block(self, b):
    self.notify_subscribers(Message.NEW_BLOCK, b) # fix later
    self.send_message(Message.NEW_BLOCK, b)
    
  def update_peer_list(self, peer_list):
    self.peer_list = peer_list
    if len(self.trans_queue) > 0:
      log.info('sending queued transactions')
      for t in self.trans_queue:
        self.send_message(Message.NEW_TRANSACTION, t)
      
  def __del__(self):
    log.info('client dying...')
    try:
      self.p2pserver.sendall(Message.QUIT)
    except:
      pass
    finally:
      self.p2pserver.close()
      if self.server:
        self.server.shutdown()
        print('server dying...')
      
  #@classmethod
  def start_server(self):
    if self.server:
      return
    log.info('starting server...')
    HOST = ''     #allow connections from any ip address
    log.info('Serving on: %s', ('', self.CLIENT_PORT))
    self.server = socketserver.TCPServer((HOST, self.CLIENT_PORT), TCPHandler)
    log.info('running...')
    self.server.serve_forever()
  
  def run(self):
    t = threading.Thread(target=self.start_server)
    t.start()

class TCPHandler(socketserver.BaseRequestHandler):
  """ Handles incoming tcp requests """
  def handle(self):
    message = self.request.recv(15).strip()
    log.info('received message from a peer..., %s', message)
    if message == Message.NEW_TRANSACTION:
      from TransactionManager.transaction import Transaction
      trans = self.request.recv(2048)
      t = Transaction()
      t.unpack(trans)
      if not t.verify():
        raise Exception('Transaction invalid!')
      else:
        log.info('Transaction has been verified')
      from P2P.client_manager import P2PClientManager
      client = P2PClientManager.getClient()
      client.queue_item_received(Message.NEW_TRANSACTION, t)
      client.notify_subscribers(Message.NEW_TRANSACTION, t)
    elif message == Message.NEW_BLOCK:
      from BlockManager.block import Block
      block = self.request.recv(2048)
      b = Block()
      b.unpack(block)
      if not b.verify():
        raise Exception('Block invalid!')
      else:
        log.info('Block has been verified')
      from P2P.client_manager import P2PClientManager
      client = P2PClientManager.getClient()
      client.queue_item_received(Message.NEW_BLOCK, b)
      client.notify_subscribers(Message.NEW_BLOCK, b)
    elif message == Message.ADD:
      from P2P.client_manager import P2PClientManager
      client = P2PClientManager.getClient()
      port = self.request.recv(128).strip()
      peer_list = pickle.loads(port)
      log.info('peer list: %s', peer_list)
      client.update_peer_list(peer_list)
      
      

if __name__ == '__main__':
  import sys
  from keystore import KeyStore
  from TransactionManager.transaction import Transaction
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