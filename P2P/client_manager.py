from P2P.p2pclient import *
from P2P.messages import Message
import logging

log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)

class P2PClientManager:
  """ Use this class to gain access to the single P2PClient object """

  p2p = None
    
  def getClient(port=65000):
    """ Returns the P2PClient object.
        If it doesn't exist, a new one is created, otherwise a reference to the existing client is returned.
    """
    if not P2PClientManager.p2p:
      P2PClientManager.p2p = P2PClient('localhost', port)
      P2PClientManager.p2p.run()
      P2PClientManager.p2p.send_message(Message.ADD)
      
    return P2PClientManager.p2p
    
  def deleteClient():
    log.info('Deleting client...')
    P2PClientManager.p2p.stop()
    P2PClientManager.p2p = None
    
if __name__ == '__main__':
  import sys
  from keystore import KeyStore
  port = sys.argv[1]
  P2PClient.CLIENT_PORT = int(port)
  trans = Transaction()
  trans.add_input(Transaction.Input(20, b'FFFFFFFF', 0))
  trans.add_output(Transaction.Output(10, KeyStore.getPublicKey())) # just pay to ourselves for now
  trans.add_input(Transaction.Input(5, b'FFFFFFFF', 0))
  s = trans.build_struct()
  
  c = P2PClient()
  c.send_message(Message.add)
  c.send_message(Message.NEW_TRANSACTION, s)
  
  import time
  time.sleep(5)
  
  trans = Transaction()
  trans.add_input(Transaction.Input(100, b'FFFFFFFF', 0))
  trans.add_output(Transaction.Output(55, KeyStore.getPublicKey())) # just pay to ourselves for now
  trans.add_input(Transaction.Input(4, b'FFFFFFFF', 0))
  s = trans.build_struct()
  c.send_message(Message.NEW_TRANSACTION, s)