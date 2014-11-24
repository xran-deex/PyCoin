#!/usr/bin/env python
import logging
from globals import LOG_LEVEL

log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)

import hashlib

# findnum2 finds a number that when hashed with 'a' returns a number begining with 24 0s, takes longer then findnum
#def findnum2(a):
#	x = hashlib.sha256()
#	x.update(a)
#	number = 0
#	str_number = str(number)
#	x.update(str_number)
#	h = x.hexdigest()
#	z = bin(long(h, 16))[2:]
#	while z[-24:] != '000000000000000000000000':
#		x = hashlib.sha256()
#		x.update(a)
#		number += 1
#		str_number = str(number)
#		x.update(str_number)
#		h = x.hexdigest()
#		z = bin(long(h, 16))[2:]
	#print z
	#print number
#	return number
	
class Miner:
  
  def __init__(self):
    self.hashnum = hashlib.sha256()
    self.b = Block()

  def handle_new_transaction(self, trans):
    self.b.handle_new_transaction(trans)
    log.info('Received new transaction')

  def findnum(self, b):
	x = hashlib.sha256()
	number = 0
	str_number = str(number)
	self.b.nonce = str_number
	self.b.computeMerkleRoot()
	x.update(self.b.pack)
	x.update(str_number)
	h = x.digest()
	while h[-3:] != '\0\0\0':
		x = hashlib.sha256()
		number += 1
		str_number = str(number)
		self.b.nonce = str_number
		x.update(self.b.pack)
		x.update(str_number)
		h = x.digest()
		if block_found:
			return -1
	return number

  def block_found(self):
  	# this is not right, still being written I think
  	client = P2PClientManager.getClient()
	if client.subscribe(NEWBLOCK, miner.handle_new_block) == True:
		return True
	else:
		return False
	
  def go(self):
  	while True:
  		self.b = Block()
  		self.b.target = 24
  		client = P2PClientManager.getClient()
  		for i in range(0, 10):
  			# still not sure how to impliment this
  			client.subscribe(miner.handle_new_transaction)
  			# should we create a new transaction here that rewards the miners work here?
  			
  		nonce = findnum(self.b)
  		if nonce < 0:
  			continue
  		elif:
  			# should we create a new transaction here that rewards the miners work or here?
  			client.broadcast_block(theBlock)
	


if __name__ == '__main__':
	m = Miner()
	m.go()
