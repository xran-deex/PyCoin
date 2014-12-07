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
    if os.path.isfile('db.db'):
      os.remove('db.db') # remove the database
    c = CoinBase() # give ourselves 100 to start with
    
  def test_create_transaction(self):

    trans = Transaction()
    trans.add_output(Transaction.Output(10, self.key)) # just pay to ourselves for now
    
    # verify the transaction
    #message = SHA256.new(str.encode('signature'))
    #verifier = PKCS1_v1_5.new(trans.output[0].pubKey)
    
    #verified = verifier.verify(message, trans.input[0].signature)
    
    self.assertIsNotNone(trans)
    
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
    
    t.verify()
    
    # find all unspent outputs for ourselves and for other.
    db = DB()
    myKey = KeyStore.getPublicKey()
    myOuts = db.getUnspentOutputs(myKey)
    othersOuts = db.getUnspentOutputs(otherKey.publickey())
    
    self.assertEqual(myOuts[0].value, 80) # we should have 80 left
    self.assertEqual(othersOuts[0].value, 20) # other should have 20 now
    
  def test_verify_transactions(self):
    otherKey = RSA.generate(2048)
    t = Transaction()
    t.add_output(Transaction.Output(20, otherKey.publickey()))
    t.finish_transaction()
    
    verified = t.verify()
    self.assertTrue(verified)
    
  def test_verify_transaction_fail(self):
    otherKey = RSA.generate(2048)
    myKey = RSA.generate(2048)
    c = CoinBase(owner=myKey)
    c.finish_transaction()
    t = Transaction(owner=myKey)
    t.add_output(Transaction.Output(20, otherKey.publickey()))
    t.finish_transaction()
    
    # purposely modify the input and sign with other's key
    i = t.input[0]
    message = SHA256.new(b'MESSAGE')
    signer = PKCS1_v1_5.new(otherKey)
    signature = signer.sign(message)
    i.signature = signature
    
    verified = t.verify()
    self.assertFalse(verified)
    
    
if __name__ == '__main__':
  unittest.main()