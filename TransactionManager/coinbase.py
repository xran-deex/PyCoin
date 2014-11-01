from transaction import Transaction

class CoinBase(Transaction):
  ''' Derived coinbase transaction '''
  
  def __init__(self):
    Transaction.__init__(self)
    print('Creating a CoinBase transaction')
    


if __name__ == '__main__':
  from input import *
  
  
  cb = CoinBase()
  cb.add_payee('Bob')
  cb.add_input(Input(20, 'sig', 1))
  cb.add_output(Output(10, 'key'))
  cb.add_input(Input(5, 'sig', 2))
  cb.build()
  cb.broadcast()