# This is a silly comment
import unittest

from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256

from keystore import *
from TransactionManager.transaction import *
from P2P.p2pclient import *
from P2P.messages import Message

class TestTransactionClass(unittest.TestCase):
  
  def setUp(self):
    self.key = KeyStore.getPublicKey()
    self.trans = Transaction()
    
  def test_create_transaction(self):
    
    self.trans.add_input(Transaction.Input(20, b'FFFFFFFF', 0))
    self.trans.add_output(Transaction.Output(10, self.key)) # just pay to ourselves for now
    self.trans.add_input(Transaction.Input(5, b'FFFFFFFF', 0))
    
    # verify the transaction
    message = SHA256.new(str.encode('signature'))
    verifier = PKCS1_v1_5.new(self.trans.output[0].pubKey)
    
    verified = verifier.verify(message, self.trans.input[0].signature)
    self.assertTrue(verified)
    
  def test_build_raw_transaction(self):
    
    self.trans.add_input(Transaction.Input(20, b'FFFFFFFF', 0))
    self.trans.add_output(Transaction.Output(10, self.key)) # just pay to ourselves for now
    self.trans.add_input(Transaction.Input(5, b'FFFFFFFF', 0))
    s = self.trans.build_struct()
    
    self.assertIsNotNone(s)
    
if __name__ == '__main__':
  unittest.main()