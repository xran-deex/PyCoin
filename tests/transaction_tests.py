import unittest

from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256

from keystore import *
from TransactionManager.transaction import *
from P2P.p2pclient import *
from P2P.p2pserver import *
from TransactionManager.coinbase import *
from P2P.messages import Message
import os
from Crypto.PublicKey import RSA
from db import DB

class TestTransactionClass(unittest.TestCase):
  
  def setUp(self):
    self.key = KeyStore.getPublicKey()
    os.remove('db.db') # remove the database
    c = CoinBase() # give ourselves 100 to start with
    
  def test_create_transaction(self):

    trans = Transaction()
    trans.add_output(Transaction.Output(10, self.key)) # just pay to ourselves for now
    
    # verify the transaction
    message = SHA256.new(str.encode('signature'))
    verifier = PKCS1_v1_5.new(trans.output[0].pubKey)
    
    verified = verifier.verify(message, trans.input[0].signature)
    self.assertTrue(verified)
    
  def test_build_raw_transaction(self):

    trans = Transaction()
    trans.add_output(Transaction.Output(10, self.key)) # just pay to ourselves for now
    trans.add_input(Transaction.Input(5, b'FFFFFFFF', 0))
    s = trans.finish_transaction()
    
    self.assertIsNotNone(s)
    
  def test_coinbase_transaction_with_2_transactions(self):
    
    otherKey = RSA.generate(2048)
    
    # create a coinbase transaction, a regulat transaction and send the output to 'otherkey'
    
    t = Transaction()
    t.add_output(Transaction.Output(20, otherKey.publickey())) # give other 20
    t.finish_transaction()
    
    # find all unspent outputs for ourselves and for other.
    db = DB()
    myKey = KeyStore.getPublicKey()
    myOuts = db.getUnspentOutputs(myKey)
    othersOuts = db.getUnspentOutputs(otherKey.publickey())
    
    self.assertEqual(myOuts[0].value, 80) # we should have 80 left
    self.assertEqual(othersOuts[0].value, 20) # other should have 20 now
    
    
if __name__ == '__main__':
  unittest.main()