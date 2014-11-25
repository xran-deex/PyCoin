#!/usr/bin/env python
import logging
from globals import LOG_LEVEL
from P2P.messages import Message
from BlockManager.block import Block
from P2P.client_manager import P2PClientManager
import copy

log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)

from Crypto.Hash import SHA256
	
class Miner:
  
  def __init__(self):
    self.hashnum = SHA256.new()
    self.transactions = []
    self.start_over = False
    self.b = Block()
    self.client = P2PClientManager.getClient()
    self.client.subscribe(Message.NEW_BLOCK, self.handle_new_block)
    self.client.subscribe(Message.NEW_TRANSACTION, self.handle_new_transaction)

  def handle_new_transaction(self, trans):
    self.transactions.append(trans)
    log.info('Received new transaction')
    if len(self.transactions) > 10:
      result = self.solve_proof_of_work()
      if result != -1:
        c = CoinBase()
        self.b.transactions.append(c)
        self.client.broadcast_block(self.b)
      
  def handle_new_block(self, block):
    self.start_over = True

  def solve_proof_of_work(self):
  	x = SHA256.new()
  	number = 0
  	str_number = str(number)
  	self.b.nonce = str_number
  	self.b.computeMerkleRoot()
  	self.b.transactions = copy.copy(self.transactions)
  	self.b.target = 24
  	x.update(self.b.pack())
  	x.update(str_number)
  	h = x.digest()
  	while h[-3:] != '\0\0\0':
  		x = SHA256.new()
  		number += 1
  		str_number = str(number)
  		self.b.nonce = str_number
  		x.update(self.b.pack)
  		x.update(str_number)
  		h = x.digest()
  		if self.start_over:
  			return -1
  	return number
	
  # def go(self):
  # 	while True:
  # 		self.b = Block()
  # 		self.b.target = 24
  # 		client = P2PClientManager.getClient()
  # 		for i in range(0, 10):
  # 			# still not sure how to impliment this
  # 			client.subscribe(miner.handle_new_transaction)
  # 			# should we create a new transaction here that rewards the miners work here?
  			
  # 		nonce = self.solve_proof_of_work()
  # 		if nonce < 0:
  # 			continue
  # 		elif:
  # 			# should we create a new transaction here that rewards the miners work or here?
  # 			client.broadcast_block(theBlock)
	


if __name__ == '__main__':
	m = Miner()
