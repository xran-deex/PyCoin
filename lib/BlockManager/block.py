import time, random, struct, logging
import db, utils
from globals import *
from Crypto.Hash import SHA256
from TransactionManager.transaction import Transaction
from P2P.client_manager import P2PClientManager

log = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)

class Block:
  
  def __init__(self):
    """ initializes the block """
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
    self.target = 20
    self.hash = None
    self.client = P2PClientManager.getClient()
    
  def add_transaction(self, trans):
    """ adds a new transaction to this block's list 

    params:
      trans -> the transaction object to add
    """
    if not isinstance(trans, Transaction):
      raise Exception('Not a Transaction object!')
    for t in self.transactionList:
      if t.hash_transaction() == trans.hash_transaction():
        return
    log.debug('Adding trans to block: %s', trans.hash_transaction())
    self.transactionList.append(trans)
    
  def computeMerkleRoot(self):
    self.HashMerkleRoot = Utils.buildMerkleTree(self.transactionList)
    
  def getPreviousBlockHash(self):
    """ retrieves the previous block hash from the database """
    return self.db.getLatestBlock()[0]
  
  def pack(self, withoutReward=False):
    """ Serializes the block into a byte array """
    b = bytearray()
    b.extend(self.HashPrevBlock) #32
    b.extend(struct.pack('I', self.nonce)) #4
    b.extend(struct.pack('B', self.target)) #1
    if withoutReward:
      num = len(self.transactionList) - 1
    else:
      num = len(self.transactionList)
    b.extend(struct.pack('B', num)) #1
    for i in range(num):
      b.extend(self.transactionList[i].hash_transaction()) # 32
    return b
  
  def unpack(self, buf):
    """ Deserializes a byte array into this block object """
    offset = 0
    self.HashPrevBlock = buf[offset:offset+32]
    offset += 32
    self.nonce = struct.unpack_from('I', buf, offset)[0]
    offset += 4
    self.target = struct.unpack_from('B', buf, offset)[0]
    offset += 1
    num_trans = struct.unpack_from('B', buf, offset)[0]
    offset += 1
    for i in range(num_trans):
      h = buf[offset:offset+32]
      log.debug('Unpacking: ', h)
      trans = self.db.getTransactionByHash(h)
      self.transactionList.append(trans)
      offset += 32
    log.debug('Block hash: %s', self.hash_block(hex=True, withoutReward=False))
    log.debug('Block nonce: &d', self.nonce)
    log.info('Block unpacked')
    
  def store_block(self):
    self.db.insertBlock(self)
    
  def hash_block(self, hex=False, withoutReward=False):
    """ hashes the block """
    b = bytearray()
    b.extend(self.pack(withoutReward=withoutReward))
    self.hash = SHA256.new(b)
    if hex:
      return self.hash.hexdigest()
    return self.hash.digest()
    
  def finish_block(self):
    """ verifies the block, then broadcasts it """
    v = self.verify()
    if v:
      self.client.broadcast_block(self, ignore=True)
      log.debug('Block verified')
      self.store_block()
    
  def verify(self, debug=False):
    """ verifies the block """
    log.debug('Finishing block')
    verified = False
    if debug:
      log.info('Block hash: %s', self.hash_block(hex=True))
    for t in self.transactionList:
      if not t.verify(debug=debug):
        log.warn('Invalid transaction in block')
        return False
    if not self.test_hash(self.hash_block(withoutReward=False), self.target):
      log.warn('Block has doesn\'t match target!')
      return False
    prevBlock = self.db.getBlock(self.HashPrevBlock)
    if prevBlock:
      log.debug('Verifying previous block')
      return prevBlock.verify(debug=debug)
    return True
    
  def test_hash(self, hash, target):
    """ check if the last 'target' bits are zeros """
    int_hash = int(struct.unpack_from('I', hash[-4:])[0])
    low = (int_hash & -int_hash)
    lowBit = -1
    while (low):
      low >>= 1
      lowBit += 1
    if lowBit == target:
      log.info(bin(int_hash))
    return lowBit == target
  
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
