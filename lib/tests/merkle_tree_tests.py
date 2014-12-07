import unittest
from Crypto.Hash import SHA256
from utils import Utils

class TestUtilClass(unittest.TestCase):
  
  def setUp(self):
    pass
  
  def test_build_merkle_tree_odd_nodes(self):
    h1 = SHA256.new()
    h2 = SHA256.new()
    h3 = SHA256.new()
    h1.update(b'hello')
    h2.update(b'world')
    h3.update(b'blah')
    hashList = [h1.digest(), h2.digest(), h3.digest()]
    merkleRoot = Utils.buildMerkleTree(hashList)
    self.assertIsNotNone(merkleRoot)
    
  def test_build_merkle_tree_even_nodes(self):
    h1 = SHA256.new()
    h2 = SHA256.new()
    h3 = SHA256.new()
    h4 = SHA256.new()
    h1.update(b'hello')
    h2.update(b'world')
    h3.update(b'blah')
    h4.update(b'blah2')
    hashList = [h1.digest(), h2.digest(), h3.digest(), h4.digest()]
    merkleRoot = Utils.buildMerkleTree(hashList)
    self.assertIsNotNone(merkleRoot)
    
if __name__ == '__main__':
  unittest.main()