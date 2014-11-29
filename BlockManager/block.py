import time, random, struct, logging
import db, utils
from globals import *
from Crypto.Hash import SHA256
from TransactionManager.transaction import Transaction

log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)

class Block:
  
  def __init__(self, prev):
    self.HashPrevBlock = prev
    self.HashMerkleRoot = None
    self.timestamp = int(time.time())
    #self.target = random.getrandbits(64)
    self.nonce = random.getrandbits(32)
    self.transactionList = []
    self.target = 2
    
  def add_transaction(self, trans):
    if not isinstance(trans, Transaction):
      raise Exception('Not a Transaction object!')
    self.transactionList.append(trans)
    
  def computeMerkleRoot(self):
    self.HashMerkleRoot = Utils.buildMerkleTree(self.transactionList)
    
  def hash_block(self):
    h = SHA256.new()
    h.update(self.pack())
    return h.digest()
    
  def getPreviousBlockHash(self):
    d = db.DB()
    return d.getLatestBlock()[0]
  
  def pack(self):
    """ Serializes the block into a byte array """
    b = bytearray()
    b.extend(self.HashPrevBlock) #32
    b.extend(struct.pack('I', self.nonce)) #4
    b.extend(struct.pack('B', self.target)) #1
    b.extend(struct.pack('B', len(self.transactionList))) #1
    for t in self.transactionList:
      b.extend(t.hash_transaction()) # 32
    return b
  
  def unpack(self, buf):
    """ Deserializes a byte array into this block object """
    offset = 0
    self.HashPrevBlock = buf[offset:offset+32]
    offset += 32
    self.nonce = struct.unpack_from('I', buf, offset)[0]
    offset += 4
    num_trans = struct.unpack_from('B', buf, offset)[0]
    offset += 1
    for i in range(num_trans):
      t = Transaction()
      h = buf[offset:offset+32]
      t.hash = SHA256.new(h)
      offset += 32
    log.info('Block unpacked')
    
  def verify(self):
    return True
  
if __name__ == '__main__':
  b = Block()
  print(b.getPreviousBlockHash())
