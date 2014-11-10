from TransactionManager.transaction import Transaction
import keystore
import random, os

class CoinBase(Transaction):
  ''' Derived coinbase transaction '''
  
  COINBASE_REWARD = 100
  
  def __init__(self):
    Transaction.__init__(self)
    print('Creating a CoinBase transaction')
    # n is 2^32 -1  for coinbase
    n = 2**32 - 1
    # prev trans is 0 for coinbase
    i = Transaction.Input(CoinBase.COINBASE_REWARD, 0, n)
    
    # 32 random bits for the coinbase field
    i.coinbase = random.getrandbits(32)
    super(CoinBase, self).add_input(i)
    super(CoinBase, self).add_output(Transaction.Output(CoinBase.COINBASE_REWARD, keystore.KeyStore.getPublicKey()))
    
  def add_input(self):
    ''' coinbase transactions only have outputs. input is determined.'''
    pass
  
  def add_output(self, output):
    pass


if __name__ == '__main__':
  
  cb = CoinBase()
  cb.add_output(Transaction.Output(10, keystore.KeyStore.getPublicKey()))
  print(cb)
  #cb.broadcast()