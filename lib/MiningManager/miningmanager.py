#!/usr/bin/env python
import logging, struct
from globals import LOG_LEVEL
from P2P.messages import Message
from BlockManager.block import Block
from TransactionManager.coinbase import CoinBase
from P2P.client_manager import P2PClientManager
import copy, threading
from TransactionManager.transaction import Transaction

log = logging.getLogger()
log.setLevel(LOG_LEVEL)

from Crypto.Hash import SHA256
import random
	
class Miner:
  
  INVALID = -1
  
  def __init__(self):
    """ initializes the miner object """
    self.hashnum = SHA256.new()
    self.transactions = []
    self.start_over = False
    self.isMining = False
    
    self.client = P2PClientManager.getClient()
    self.client.subscribe(Message.NEW_BLOCK, self.handle_new_block)
    self.client.subscribe(Message.NEW_TRANSACTION, self.handle_new_transaction)
    self.mining_thread = None

  def handle_new_transaction(self, trans):
    """ a callback function that is called when a new transaction is received
    from the p2p client

    params:
      trans -> the new transaction
    """
    if not isinstance(trans, Transaction):
      raise Exception('Not a Transaction object!')
    self.transactions.append(trans)
    log.debug('Received new transaction')
    if len(self.transactions) > 5 and not self.isMining:
      self.mining_thread = threading.Thread(target=self.solve_on_thread)
      self.mining_thread.start()
        
  def solve_on_thread(self):
    """ solves the POW and creates a new coinbase transaction when solved. """
    self.coinbase = CoinBase()
    self.transactions.append(self.coinbase)
    self.b = Block()
    result = self.solve_proof_of_work()
    if self.start_over:
        self.start_over = False
        log.debug('Mining stopped')
        self.isMining = False
        return
    if result:
      self.transactions = []
      log.info('Block solution found!, %d', self.b.nonce)
      self.client.broadcast_info('Block solution found')
      log.info('Block hash: %s', self.b.hash_block(hex=True, withoutReward=False))
      self.broadcast_info('Block solution found!')
      if self.start_over:
        self.start_over = False
        self.isMining = False
        log.debug('Mining stopped')
        return
      
      self.coinbase.finish_transaction()
      self.b.finish_block()
      self.isMining = False
      
  def handle_new_block(self, block):
    """ a callback method that will be called when a new block is received
    from the p2p client.

    params:
      block -> the new block
    """
    log.debug('Received new block')
    self.start_over = True
    self.remove_queue_transactions(block)
    self.isMining = False
    
  def remove_queue_transactions(self, block):
    """ removes any transactions from the queue that were
    already included in the incoming block

    params:
      block -> the received block
    """
    toBeRemoved = []
    for t in block.transactionList:
      for trans in self.transactions:
        if t.hash_transaction() == trans.hash_transaction():
          toBeRemoved.append(trans)
    for t in toBeRemoved:
      log.debug('Remove from queue: ', t.hash_transaction())
      self.transactions.remove(t)

  def solve_proof_of_work(self):
    """ solves the proof of work problem
    Starting with the random nonce, this thread will increment this
    value and hash the block with the nonce and test to see if the
    hash ends with the 'target' amount of zeros. If not, the nonce
    is incremented and a new hash is produced

    """
    log.info('Mining started...')
    self.client.broadcast_info('Mining started')
    self.isMining = True
    hash = SHA256.new()
    
    #self.b.computeMerkleRoot()
    for t in self.transactions:
      self.b.add_transaction(t)

    # create an array of target-length bytes
    target = bytes(self.b.target)
    hash.update(self.b.pack())
    digest = hash.digest()

    while not self.test_hash(digest, self.b.target):
      hash = SHA256.new()
      # update the nonce
      self.b.nonce += 1

      hash.update(self.b.pack())
      digest = hash.digest()
      if self.start_over:
        self.start_over = False
        return False
    return True
    
  def broadcast_info(self, info):
    """ subscribe to mining info 

    params:
      info -> the message to send to the subscriber callback
    """
    self.subscriber(info)
    
  def subscribe(self, subscriber):
    """ adds a subscriber to this Miner

    params:
      subscriber -> A callback function that will receive the info message
    """
    self.subscriber = subscriber
    
  def test_hash(self, hash, target):
    """ check if the last 'target' bits are zeros """
    int_hash = int(struct.unpack_from('I', hash[-4:])[0])
    low = (int_hash & -int_hash)
    lowBit = -1
    while (low):
      low >>= 1
      lowBit += 1
    if lowBit == target:
      log.info(bin(int_hash))
    return lowBit == target
    
  def verify_block_chain(self, debug=False):
    from db import DB
    d = DB()
    log.info('Verifying blockchain...')
    self.client.broadcast_info('Verifying blockchain')
    latest_block_hash = d.getLatestBlockHash()
    if not latest_block_hash:
      return True
    latest_block = d.getBlock(latest_block_hash)
    return latest_block.verify(debug=debug)

if __name__ == '__main__':
  import sys, time
  from keystore import KeyStore
  from Crypto.PublicKey import RSA
  from Crypto import Random
  r = Random.new().read
  otherKey = RSA.generate(2048, r)
  myKey = RSA.generate(2048, r)
  from TransactionManager.coinbase import CoinBase
  m = Miner()
  c = CoinBase(owner=myKey)
  c.finish_transaction()

  t = Transaction(owner=myKey)

  t.add_output(Transaction.Output(20, myKey.publickey()))
  t.finish_transaction()
  
  
  b = Block()
  b.add_transaction(t)
  b.finish_block()
  
  t = Transaction(owner=myKey)

  t.add_output(Transaction.Output(25, myKey.publickey()))
  t.finish_transaction()
  
  b2 = Block()
  b2.add_transaction(t)
  b2.finish_block()
