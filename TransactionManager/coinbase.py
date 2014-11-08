from transaction import Transaction
import keystore
import random

class CoinBase(Transaction):
  ''' Derived coinbase transaction '''
  
  def __init__(self):
    Transaction.__init__(self)
    print('Creating a CoinBase transaction')
    
    # prev trans is 0 for coinbase
    i = Transaction.Input(20, 0)
    # n is 2^32 -1  for coinbase
    i.n = 2**32 - 1
    # 32 random bits for the coinbase field
    i.coinbase = random.getrandbits(32)
    super(CoinBase, self).add_input(i)
    
  def add_input(self):
    ''' coinbase transactions only have outputs. input is determined.'''
    pass
  
  def add_output(self, output):
    self.output.append(output)


if __name__ == '__main__':
  
  cb = CoinBase()
  cb.add_output(Transaction.Output(10, keystore.KeyStore.getPublicKey()))
  cb.build()
  cb.broadcast()