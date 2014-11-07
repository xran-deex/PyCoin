from transaction import Transaction
import keystore

class CoinBase(Transaction):
  ''' Derived coinbase transaction '''
  
  def __init__(self):
    Transaction.__init__(self)
    print('Creating a CoinBase transaction')
    super(CoinBase, self).add_input(Transaction.Input(20, 'FFFFFFFF'))
    
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