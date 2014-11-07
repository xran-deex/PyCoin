from P2P.p2pclient import *
from P2P.messages import Message

class P2PClientManager:
  """ Use this class to gain access to the single P2PClient object """

  p2p = None
    
  def getClient():
    """ Returns the P2PClient object.
        If it doesn't exist, a new one is created, otherwise a reference to the existing client is returned.
    """
    if not P2PClientManager.p2p:
      P2PClientManager.p2p = P2PClient()
      P2PClientManager.p2p.send_message(Message.ADD)
      P2PClient.run()

    return P2PClientManager.p2p
    
if __name__ == '__main__':
  import sys
  from keystore import KeyStore
  port = sys.argv[1]
  P2PClient.SERVER_PORT = int(port)
  trans = Transaction()
  trans.add_input(Transaction.Input(20, b'FFFFFFFF'))
  trans.add_output(Transaction.Output(10, KeyStore.getPublicKey())) # just pay to ourselves for now
  trans.add_input(Transaction.Input(5, b'FFFFFFFF'))
  s = trans.build_struct()
  
  c = P2PClient()
  c.send_message(Message.add)
  c.send_message(Message.NEW_TRANSACTION, s)
  
  import time
  time.sleep(5)
  
  trans = Transaction()
  trans.add_input(Transaction.Input(100, b'FFFFFFFF'))
  trans.add_output(Transaction.Output(55, KeyStore.getPublicKey())) # just pay to ourselves for now
  trans.add_input(Transaction.Input(4, b'FFFFFFFF'))
  s = trans.build_struct()
  c.send_message(Message.NEW_TRANSACTION, s)