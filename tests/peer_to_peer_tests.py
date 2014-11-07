import unittest
from TransactionManager.transaction import *
from P2P.p2pserver import *
from P2P.p2pclient import *

class TestPeerToPeerClass(unittest.TestCase):
  
  def setUp(self):
    pass
    
  def test_create_client_server(self):
    t = threading.Thread(target=self.start_thread)
    t.start()
    P2PClient.SERVER_PORT = int(22222)
    trans = Transaction()
    trans.add_input(Transaction.Input(20, b'FFFFFFFF'))
    trans.add_output(Transaction.Output(10, KeyStore.getPublicKey())) # just pay to ourselves for now
    trans.add_input(Transaction.Input(5, b'FFFFFFFF'))
    s = trans.build_struct()
    
    c = P2PClient()
    c.send_message(Message.add)
    c.send_message(Message.new_transaction, s)
    
    c = None
    p = None
    
  def start_thread(self):
    P2PServer()
    
if __name__ == '__main__':
  unittest.main()