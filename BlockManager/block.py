import time, random
import db

class Block:
  
  def __init__(self):
    self.HashPrevBlock = None
    self.HashMerkleRoot = None
    self.timestamp = int(time.time())
    self.target = random.getrandbits(64)
    self.nonce = random.getrandbits(32)
    self.transactionList = []
    
  def add_transaction(self, trans):
    self.transactionList.append(trans)
    
  def getPreviousBlockHash(self):
    d = db.DB()
    return d.getLatestBlock()[0]
  
  def pack(self):
    """ Serializes the block into a byte array """
    b = bytearray()
    
    return b
  
  def unpack(self, buf):
    """ Deserializes a byte array into this block object """
    pass
  
if __name__ == '__main__':
  b = Block()
  print(b.getPreviousBlockHash())