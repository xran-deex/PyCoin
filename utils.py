from Crypto.Hash import SHA256

class Utils:
  
  def buildMerkleTree(hashList):
    """ build a merkle tree from a list of hashes
    
    Returns: the hash of the root
    """
    result = SHA256.new()
    if len(hashList) % 2 == 1:
      lastHash = hashList.pop()
      result.update(lastHash + lastHash)
    while len(hashList) != 0:
      lastHash = hashList.pop()
      nextToLastHash = hashList.pop()
      result.update(lastHash + nextToLastHash)
    return result.digest()
    
    
if __name__ == '__main__':
  h1 = SHA256.new()
  h2 = SHA256.new()
  h3 = SHA256.new()
  h1.update(b'hello')
  h2.update(b'world')
  h3.update(b'blah')
  hashList = [h1.digest(), h2.digest(), h3.digest()]
  print(Utils.buildMerkleTree(hashList))