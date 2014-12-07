from TransactionManager.transaction import Transaction
import keystore
import random, os
from Crypto.Hash import SHA256
import struct

import logging
from globals import LOG_LEVEL

log = logging.getLogger()
log.setLevel(LOG_LEVEL)

class CoinBase(Transaction):
  ''' Derived coinbase transaction '''
  
  COINBASE_REWARD = 10
  
  def __init__(self, owner=None, amt=None):
    Transaction.__init__(self, owner)
    log.debug('Creating a CoinBase transaction')
    if not owner:
      self.owner = keystore.KeyStore.getPrivateKey()
    else:
      self.owner = owner
    # n is 2^8 -1  for coinbase
    n = 2**8 - 1
    # prev trans is 0 for coinbase
    if not amt:
      amt = CoinBase.COINBASE_REWARD
    i = Transaction.Input(amt, self.get_zero_bytes(), n, owner=self.owner)
    
    # 32 random bits for the coinbase field
    random.seed()
    i.coinbase = random.getrandbits(32)
    self.add_input(i)
    out = Transaction.Output(amt, self.owner.publickey())
    self.add_output(out)
    
  def get_zero_bytes(self):
    return bytes(struct.pack('I', 0) * 8)
    
  def add_input(self, i):
    ''' coinbase transactions only have outputs. input is determined.'''
    self.input.append(i)
  
  def add_output(self, output):
    """ Adds an output to this transaction
    
    Args:
      output: an Transaction.Output object that will be added to this transaction
      
    Returns:
      Self, for use as a factory type builder.
    """
    log.debug('creating output... %d', output.value)
    self.output.append(output)
    output.n = len(self.output)
    output.transaction = self.hash_transaction()

    return self
  
  def hash_zero(self):
    hash = SHA256.new()
    hash.update(struct.pack('I', 0))
    return hash.digest()


if __name__ == '__main__':
  
  cb = CoinBase()
  cb.add_output(Transaction.Output(10, keystore.KeyStore.getPublicKey()))
  print(cb)
  #cb.broadcast()