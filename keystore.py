## Edit
from Crypto.PublicKey import RSA
import os.path

class KeyStore:
  """Manages storing and retrieving the user's public/private key
  
  Attributes:
    _key_file: the name of the on-disk file that stores the private key
  """
  
  _key_file = 'wallet.dat'

  def getPublicKey():
    """Gets the public key from file, or creates a new one is it doesn't exist"""
    if(os.path.isfile(KeyStore._key_file)):
      f = open(KeyStore._key_file, 'rb')
      public = RSA.importKey(f.read())
      f.close()
      
    else:
      f = open(KeyStore._key_file, 'wb')
      public = RSA.generate(2048)
      f.write(public.exportKey())
      f.close()
      
    return public.publickey()
    
  def getPrivateKey():
    """Gets the public key from file, or creates a new one is it doesn't exist"""
    if(os.path.isfile(KeyStore._key_file)):
      f = open(KeyStore._key_file, 'rb')
      public = RSA.importKey(f.read())
      f.close()
      
    else:
      f = open(KeyStore._key_file, 'wb')
      public = RSA.generate(2048)
      f.write(public.exportKey())
      f.close()
      
    return public
  
  def get_balance(pubKey=None):
    from db import DB
    db = DB()
    if pubKey:
      unspent = db.getUnspentOutputs(pubKey)
    else:
      unspent = db.getUnspentOutputs(KeyStore.getPublicKey())
    balance = 0
    print(unspent)
    for o in unspent:
      balance += o.value
    return balance
    
