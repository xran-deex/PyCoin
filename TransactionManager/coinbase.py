from TransactionManager.transaction import Transaction
import keystore
import random, os
from Crypto.Hash import SHA256
import struct

import logging
from globals import LOG_LEVEL

log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)

class CoinBase(Transaction):
  ''' Derived coinbase transaction '''
  
  COINBASE_REWARD = 100
  
  def __init__(self, owner=None):
    Transaction.__init__(self)
    log.info('Creating a CoinBase transaction')
    if not owner:
      self.owner = keystore.KeyStore.getPrivateKey()
    else:
      self.owner = owner
    # n is 2^8 -1  for coinbase
    n = 2**8 - 1
    # prev trans is 0 for coinbase
    i = Transaction.Input(CoinBase.COINBASE_REWARD, self.get_zero_bytes(), n, owner=self.owner)
    
    # 32 random bits for the coinbase field
    i.coinbase = random.getrandbits(32)
    self.add_input(i)
    out = Transaction.Output(CoinBase.COINBASE_REWARD, self.owner.publickey())
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
    log.info('creating output... %d', output.value)
    self.output.append(output)
    output.n = len(self.output)
    #output.transaction = self.hash_transaction()

    #from db import DB
    #db = DB()
    #db.insertUnspentOutput(output, self)
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