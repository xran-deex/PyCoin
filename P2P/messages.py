class Message:
  ''' RPC messages '''
  
  # sent to add a client to the list of peers
  ADD = b'ADD'
  
  # sent when broadcasting a new transaction
  NEW_TRANSACTION = b'NEW_TRANSACTION'
  
  # sent to end a connection
  QUIT = b'QUIT'
  
  # sent to remove a client from the peer list
  REMOVE = b'REMOVE'