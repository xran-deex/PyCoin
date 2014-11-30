from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Button, Style
#from MiningManager.miningmanager import Miner
#from P2P.client_manager import P2PClientManager
#from TransactionManager.transaction import Transaction
#from TransactionManager.coinbase import CoinBase
import threading, random
#from keystore import KeyStore
from Crypto.PublicKey import RSA
#from P2P.messages import Message
#from db import DB

class PyCoin(Frame):

    coin_balance = 0
    
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.quit)
        self.coin_balance = StringVar(self.parent, '0')
        d = DB()
        self.initApp()
        self.setupGUI()
        
    def quit(self):
      print('quiting...')
      P2PClientManager.deleteClient()
      #self.miner.stop()
      self.parent.destroy()

    def initApp(self):
        #Connect Here
        client = P2PClientManager.getClient(port=random.randint(40000, 60000))
        client.subscribe(Message.NEW_TRANSACTION, self.update_balance)
        t = threading.Thread(target=self.start_miner)
        t.start()
        #c = CoinBase()
        #c.finish_transaction()
        #Get balance, Save to variable below
        self.coin_balance.set(str(KeyStore.get_balance()))
        print(KeyStore.getPublicKey().exportKey())
        print("App initiated")
        
    def start_miner(self):
      self.miner = Miner()

    def update_balance(self, t):

        self.coin_balance.set(str(KeyStore.get_balance()))
    
    def setupGUI(self):
      
        self.parent.title("PyCoin")
        self.pack(fill=BOTH, expand=1)

        #Labeled Frames for Status and Send
        lf = LabelFrame(self, text="Send BitCoins")
        lf.pack(side=BOTTOM, fill="both", expand="yes", padx=7, pady=7)

        lf2 = LabelFrame(self, text="BitCoin Status")
        lf2.pack(side=TOP, fill="both", expand="yes", padx=7, pady=7)
        
        #Labels for Bitcoin balance
        self.balanceHeading = Label(lf2, text="BitCoin Balance:",
                             font = "Helvetica 20")
        self.balanceHeading.pack()
        self.balance = Label(lf2, textvariable=self.coin_balance, font="Helvetica 20")
        self.balance.pack()

        
        
        #Label and Text field for BitCoin Amount

        self.amtFrame = Frame(lf);
        self.amtFrame.pack()
        
        self.label = Label(self.amtFrame, text="BitCoin Amount :")
        self.label.pack(side=LEFT)
        
        self.amountBox = Entry(self.amtFrame, bd=2)
        self.amountBox.pack(side=LEFT, pady=10, fill=X)
        

        #Label and Text filed for Reciever Key
        self.label = Label(lf, text="Receivers Public Key:")
        self.label.pack()

        self.recieverKey = Text(lf, width=30, height=10)
        self.recieverKey.pack()

        #Send Button
        self.sendBtn = Button(lf, text='\nSend BitCoin(s)\n', command=self.sendCoins)
        self.sendBtn.pack(fill=X, pady=5)

        #Status Bar
        #status = Label(lf, text="Ready", bd=1, relief=SUNKEN, anchor=W)
        #status.pack(side=BOTTOM, fill=X)

        print("GUI Initiated")

    
    #Send Button Callback Function
    def sendCoins(self):
        sendAmt = self.amountBox.get()      	    #Amount to send
        recvKey = self.recieverKey.get("1.0",'end-1c')   #recievers public key
        temp = ''
        skip = False
        for i in range(len(recvKey)):
            if recvKey[i] == '\\' and recvKey[i+1] == 'n':
                temp += '\n'
                skip = True
            elif skip:
                skip = False
                continue
            else:
                temp += recvKey[i]

        recvPubKey = RSA.importKey(bytes(temp, 'ascii'))

        if not sendAmt:
            messagebox.showwarning("Warning", "Please enter a BitCoin amount.")
        elif len(recvKey) <= 1:
            messagebox.showwarning("Warning", "Please enter the receivers key.")
        else:
            result = messagebox.askyesno("Send Confirmation", 'Sending {} BitCoins to reciever:\n {}'.format(sendAmt, recvKey))

            if result == True:
              print('Sending {} BitCoins to reciever:\n {}'.format(sendAmt, recvKey))
              t = Transaction()
              t.add_output(Transaction.Output(int(sendAmt), recvPubKey))
              t.finish_transaction()
            else:
              None
            self.amountBox.delete(0,END)
           
        
def main():
  
    root = Tk()
    app = PyCoin(root)
    
    root.mainloop()


if __name__ == '__main__':
    main()
