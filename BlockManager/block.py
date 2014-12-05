import time, random, struct, logging
import db, utils
from globals import *
from Crypto.Hash import SHA256
from TransactionManager.transaction import Transaction

log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)

class Block:
  
  def __init__(self):
    from db import DB
    self.db = DB()
    prev = self.db.getLatestBlockHash()
    if not prev:
      self.HashPrevBlock = bytes(32)
    else:
      self.HashPrevBlock = prev
    self.HashMerkleRoot = None
    self.timestamp = int(time.time())
    #self.target = random.getrandbits(64)
    self.nonce = random.getrandbits(32)
    self.transactionList = []
    self.target = 16
    self.hash = None
    
  def add_transaction(self, trans):
    if not isinstance(trans, Transaction):
      raise Exception('Not a Transaction object!')
    self.transactionList.append(trans)
    
  def computeMerkleRoot(self):
    self.HashMerkleRoot = Utils.buildMerkleTree(self.transactionList)
    
  def getPreviousBlockHash(self):
    return self.db.getLatestBlock()[0]
  
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
    
  def store_block(self):
    self.db.insertBlock(self)
    
  def hash_block(self, hex=False):
    if not self.hash:
      b = bytearray()
      b.extend(self.HashPrevBlock) #32
      b.extend(struct.pack('I', self.nonce)) #4
      b.extend(struct.pack('B', self.target)) #1
      b.extend(struct.pack('B', len(self.transactionList))) #1
      self.hash = SHA256.new(b)
    if hex:
      return self.hash.hexdigest()
    return self.hash.digest()
    
  def finish_block(self):
    v = self.verify()
    if v:
      log.debug('Block verified')
      self.store_block()
    
  def verify(self):
    verified = False
    for t in self.transactionList:
      if not t.verify():
        return False
    prevBlock = self.db.getBlock(self.HashPrevBlock)
    if prevBlock:
      log.debug('Verifying previous block')
      return prevBlock.verify()
    return True
    
  
if __name__ == '__main__':
  import sys, time
  from keystore import KeyStore
  from Crypto.PublicKey import RSA
  from Crypto import Random
  r = Random.new().read
  otherKey = RSA.generate(2048, r)
  myKey = RSA.generate(2048, r)
  from TransactionManager.coinbase import CoinBase
  c = CoinBase(owner=myKey)
  c.finish_transaction()

  t = Transaction(owner=myKey)

  t.add_output(Transaction.Output(20, myKey.publickey()))
  t.finish_transaction()
  
  
  b = Block()
  b.add_transaction(t)
  b.finish_block()
  
  t = Transaction(owner=myKey)

  t.add_output(Transaction.Output(25, myKey.publickey()))
  t.finish_transaction()
  
  b2 = Block()
  b2.add_transaction(t)
  b2.finish_block()
  
  t = Transaction(owner=myKey)

  t.add_output(Transaction.Output(25, myKey.publickey()))
  t.finish_transaction()
  
  b2 = Block()
  b2.add_transaction(t)
  b2.finish_block()
  #print(b.getPreviousBlockHash())
