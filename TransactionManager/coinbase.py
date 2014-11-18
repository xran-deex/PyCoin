from TransactionManager.transaction import Transaction
import keystore
import random, os
from Crypto.Hash import SHA256
import struct

class CoinBase(Transaction):
  ''' Derived coinbase transaction '''
  
  COINBASE_REWARD = 100
  
  def __init__(self):
    Transaction.__init__(self)
    print('Creating a CoinBase transaction')
    # n is 2^8 -1  for coinbase
    n = 2**8 - 1
    # prev trans is 0 for coinbase
    i = Transaction.Input(CoinBase.COINBASE_REWARD, 0, n)
    
    # 32 random bits for the coinbase field
    i.coinbase = random.getrandbits(32)
    self.add_input(i)
    out = Transaction.Output(CoinBase.COINBASE_REWARD, keystore.KeyStore.getPublicKey())
    out.transaction = self.hash_zero()
    super(CoinBase, self).add_output(out)
    
  def add_input(self, i):
    ''' coinbase transactions only have outputs. input is determined.'''
    self.input.append(i)
  
  def add_output(self, output):
    pass
  
  def hash_zero(self):
    hash = SHA256.new()
    hash.update(struct.pack('I', 0))
    return hash.digest()


if __name__ == '__main__':
  
  cb = CoinBase()
  cb.add_output(Transaction.Output(10, keystore.KeyStore.getPublicKey()))
  print(cb)
  #cb.broadcast()