import socket, pickle, threading, socketserver
from P2P.messages import Message
from P2P.p2pserver import P2PServer
from Crypto.Hash import SHA
from keystore import KeyStore

import logging
from globals import LOG_LEVEL

log = logging.getLogger()
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
    log.debug('Creating client on port... %d', self.CLIENT_PORT)
    self.p2pserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    log.debug('Connecting to host...')
    self.p2pserver.connect((host, P2PClient.PORT))
    self.myIP = self.p2pserver.getsockname()[0] # the ip of this machine
    self.myPublicKey = KeyStore.getPublicKey().exportKey()
    self.trans_queue = []
    self.received_trans = []
    self.received_blocks = []
    self.peer_list = []
    self.trans_listeners = []
    self.block_listeners = []
    self.keyTable = {}
    
  def broadcast_info(self, info):
    self.subscriber(info)
    
  def subscribe_to_info(self, callback):
    self.subscriber = callback

  def build_key_table(self):
    self.keyTable = {}
    for addr, port, key in self.peer_list:
      self.keyTable[SHA.new(key).hexdigest()] = key
    
  def send_message(self, message, payload=None):
    log.debug('Sending message...')
    import time
    if message == Message.ADD:
      # if the message is add, send an 'ADD' message to the p2p server
      self.p2pserver.sendall(message)
      time.sleep(0.1)
      self.p2pserver.sendall(pack('I', self.CLIENT_PORT) + self.myPublicKey)
      self.peer_list = pickle.loads(self.p2pserver.recv(1024).strip())
      self.build_key_table()
      
    elif message == Message.NEW_TRANSACTION:
      # if the message is 'NEW_TRANSACTION', send the message and payload (packed transaction) to each peer
      if len(self.peer_list) == 1 and self.peer_is_self(self.peer_list[0]):
        self.queue_transaction(payload)
        log.debug('queued transaction')
        return
      for peer in self.peer_list:
        
        # make sure we don't send the transaction back to ourselves.
        if self.peer_is_self(peer):
          continue
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log.debug('Connecting to peer %s', peer)
        s.connect((peer[0], peer[1]))
        log.debug('sent message: %s', message)
        s.sendall(message)
        time.sleep(0.1)
        log.debug('sending payload...')
        s.sendall(payload)
        s.close()
        
    elif message == Message.NEW_BLOCK:
      # handle a new block
      for peer in self.peer_list:
        
        if self.peer_is_self(peer):
          continue
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log.debug('Connecting to peer %s', peer)
        s.connect((peer[0], peer[1]))
        log.debug('sent message: %s', message)
        s.sendall(message)
        time.sleep(0.1)
        log.debug('sending payload...')
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
      log.debug('miner subscribed')
    
  def notify_subscribers(self, message_type, trans):
    if message_type == Message.NEW_TRANSACTION:
      for callback in self.trans_listeners:
        callback(trans)
    elif message_type == Message.NEW_BLOCK:
      for callback in self.block_listeners:
        callback(trans)
  
  def broadcast_transaction(self, t):
    
    self.send_message(Message.NEW_TRANSACTION, t.pack(withSig=True))
    self.notify_subscribers(Message.NEW_TRANSACTION, t)
    
  def broadcast_block(self, b, ignore=False):
    if not ignore:
      self.notify_subscribers(Message.NEW_BLOCK, b) # fix later
    self.send_message(Message.NEW_BLOCK, b.pack())
    
  def update_peer_list(self, peer_list):
    self.peer_list = peer_list
    self.build_key_table()

    if len(self.trans_queue) > 0:
      log.debug('sending queued transactions')
      for t in self.trans_queue:
        self.send_message(Message.NEW_TRANSACTION, t)
      
  def stop(self):
    log.debug('client dying...')
    try:
      self.p2pserver.sendall(Message.QUIT)
    except:
      pass
    finally:
      self.p2pserver.close()
      if self.server:
        self.server.shutdown()
        log.debug('client server dying...')

  def start_server(self):
    if self.server:
      return
    log.debug('starting server...')
    HOST = ''     #allow connections from any ip address
    log.debug('Serving on: %s', ('', self.CLIENT_PORT))
    self.server = socketserver.TCPServer((HOST, self.CLIENT_PORT), TCPHandler)
    log.debug('running...')
    self.server.serve_forever()
  
  def run(self):
    t = threading.Thread(target=self.start_server)
    t.start()

class TCPHandler(socketserver.BaseRequestHandler):
  """ Handles incoming tcp requests """
  def handle(self):
    message = self.request.recv(9).strip()
    log.debug('received message from a peer..., %s', message)
    log.info(message)
    if message == Message.NEW_TRANSACTION:
      from TransactionManager.transaction import Transaction
      trans = self.request.recv(2048)
      t = Transaction()
      t.unpack(trans, withSig=True)
      if not t.verify():
        log.warn('Invalid transaction!')
        raise Exception('Transaction invalid!')
      else:
        log.info('Transaction has been verified')
      from db import DB
      d = DB()
      d.insertTransaction(t)
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
      client.notify_subscribers(Message.NEW_BLOCK, b)
      client.queue_item_received(Message.NEW_BLOCK, b)
      
    elif message[:3] == Message.ADD:
      from P2P.client_manager import P2PClientManager
      client = P2PClientManager.getClient()
      port = self.request.recv(1024).strip()
      peer_list = pickle.loads(port)
      log.debug('peer list: %s', peer_list)
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