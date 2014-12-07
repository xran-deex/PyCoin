import unittest, os, time
from P2P.client_manager import *
from TransactionManager.coinbase import *
from MiningManager.miningmanager import *
from P2P.p2pserver import *

class TestMiningClass(unittest.TestCase):
  
  def setUp(self):
    if os.path.exists('db.db'):
      os.remove('db.db') # remove the database
    self.server = P2PServer()
  
  def test_subscribe_to_client(self):
    
    # create a miner and assert that it has no transactions queued
    miner = Miner()
    self.assertEqual(len(miner.transaction_queue), 0)
    
    time.sleep(1)

    # get a reference to the p2p client and add the miner as a subscriber
    client = P2PClientManager.getClient()
    client.subscribe(miner.handle_new_transaction)
    
    # create a new transaction that will be picked up by the miner
    c = CoinBase()
    c.finish_transaction()
    
    # the miner should now have a transaction in its queue
    self.assertEqual(len(miner.transaction_queue), 1)
    
    # kill the server...
    client.__del__()
    
if __name__ == '__main__':
  unittest.main()