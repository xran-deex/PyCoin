import unittest
from TransactionManager.transaction import *
from P2P.p2pserver import *
from P2P.p2pclient import *
from P2P.client_manager import *
import time

class TestPeerToPeerClass(unittest.TestCase):
  
  @classmethod
  def setUpClass(cls):
    P2PServer.DEBUG = False
    print('starting server...')
    cls.server = P2PServer()
    time.sleep(1)
    P2PClient.run()
  
  def setUp(self):
    pass
  
  def tearDown(self):
    pass
  
  @classmethod
  def tearDownClass(cls):
    cls.server.shutdown_server()
  
  def test_create_client(self):
    
    P2PClient.CLIENT_PORT = int(22221)
    c = P2PClient('localhost')
    c.send_message(Message.ADD)
    
    c.send_message(Message.REMOVE)
    time.sleep(2)
    
  def test_create_client_server(self):
    
    P2PClient.CLIENT_PORT = int(22222)
    trans = Transaction()
    trans.add_input(Transaction.Input(20, b'FFFFFFFF', 0))
    trans.add_output(Transaction.Output(10, KeyStore.getPublicKey())) # just pay to ourselves for now
    trans.add_input(Transaction.Input(5, b'FFFFFFFF', 0))
    s = trans.build_struct()
    
    c = P2PClient('localhost')
    c.send_message(Message.ADD)
    c.send_message(Message.ADD)
    c.send_message(Message.NEW_TRANSACTION, s)
    time.sleep(2)
    
if __name__ == '__main__':
  unittest.main()