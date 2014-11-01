import unittest

from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256

from keystore import *
from TransactionManager.transaction import *

class TestTransactionClass(unittest.TestCase):
  
  def setUp(self):
    self.key = KeyStore.getPublicKey()
    self.trans = Transaction()
    
  def test_create_transaction(self):
    
    self.trans.add_input(Transaction.Input(20))
    self.trans.add_output(Transaction.Output(10, self.key.publickey())) # just pay to ourselves for now
    self.trans.add_input(Transaction.Input(5))
    self.trans.build()
    self.trans.broadcast()
    
    # verify the transaction
    message = SHA256.new(str.encode('signature'))
    verifier = PKCS1_v1_5.new(self.trans.output[0].pubKey)
    
    verified = verifier.verify(message, self.trans.input[0].signature)
    self.assertTrue(verified)
    
if __name__ == '__main__':
  unittest.main()