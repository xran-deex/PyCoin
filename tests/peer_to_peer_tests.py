import unittest
from TransactionManager.transaction import *
from P2P.p2pserver import *
from P2P.p2pclient import *
import time

class TestPeerToPeerClass(unittest.TestCase):
  
  server = None
  
  @classmethod
  def setUpClass(cls):
    print('starting server...')
    cls.t = threading.Thread(target=TestPeerToPeerClass.start_thread)
    cls.t.start()
    time.sleep(1)
  
  def setUp(self):
    pass
    
  def tearDown(self):
    print('ending test...')
  
  def test_create_client(self):
    P2PClient.CLIENT_PORT = int(22221)
    c = P2PClient('localhost')
    del c
    
  def test_create_client_server(self):
    
    P2PClient.CLIENT_PORT = int(22222)
    trans = Transaction()
    trans.add_input(Transaction.Input(20, b'FFFFFFFF'))
    trans.add_output(Transaction.Output(10, KeyStore.getPublicKey())) # just pay to ourselves for now
    trans.add_input(Transaction.Input(5, b'FFFFFFFF'))
    s = trans.build_struct()
    
    c = P2PClient('localhost')
    c.send_message(Message.ADD)
    c.send_message(Message.NEW_TRANSACTION, s)

    
  def start_thread():
    TestPeerToPeerClass.server = P2PServer()
    
if __name__ == '__main__':
  unittest.main()