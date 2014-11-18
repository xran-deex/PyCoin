#!/usr/bin/env python

import hashlib
# test code to 1 learn python and 2 get an understanding of using sha256
# findnum finds a number that when hashed with 'a' returns a number begining with 24 0s or 3 0 bytes
def findnum(a):
	x = hashlib.sha256()
	x.update(a)
	number = 0
	str_number = str(number)
	x.update(str_number)
	h = x.digest()
	while h[-3:] != '\0\0\0':
		x = hashlib.sha256()
		x.update(a)
		number += 1
		str_number = str(number)
		x.update(str_number)
		h = x.digest()
	#print number
	return number
# findnum2 finds a number that when hashed with 'a' returns a number begining with 24 0s, takes longer then findnum
def findnum2(a):
	x = hashlib.sha256()
	x.update(a)
	number = 0
	str_number = str(number)
	x.update(str_number)
	h = x.hexdigest()
	z = bin(long(h, 16))[2:]
	while z[-24:] != '000000000000000000000000':
		x = hashlib.sha256()
		x.update(a)
		number += 1
		str_number = str(number)
		x.update(str_number)
		h = x.hexdigest()
		z = bin(long(h, 16))[2:]
	#print z
	#print number
	return number
	
class Miner:
  
  def __init__(self):
    self.transaction_queue = []
    
  def handle_new_transaction(self, trans):
    self.transaction_queue.append(trans)
    print('Received new transaction')

if __name__ == '__main__':
	argument = 'abc123'
	findnum(argument)
	findnum2(argument)
	
  