from tkinter import *
from tkinter.ttk import Button, Style

class GUI(Frame):
    
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.setup()
    
    def setup(self):
      
        self.parent.title("PyCoin")
        self.pack(fill=BOTH, expand=1)

        #Label and Text field for BitCoin Amount
        self.label = Label(self, text="Amount of Bitcoins to send:")
        #self.label.grid(column=0, row=0)
        self.label.pack()
        
        self.amountBox = Entry(self, bd=2)
        self.amountBox.pack(fill=X, pady=10)

        #Label and Text filed for Reciever Key
        self.label = Label(self, text="Recievers Public Key:")
        #self.label.grid(column=0, row=0)
        self.label.pack()

        self.recieverKey = Text(self, width=40, height=15)
        #self.recieverKey.grid(column=0, row=2)
        self.recieverKey.pack()

        #Send Button
        self.sendBtn = Button(self, text='\nSend BitCoin(s)\n', command=self.sendCoins)
        #self.sendBtn.grid(column=0, row=2)
        self.sendBtn.pack(fill=X, pady=10)

        #Status Bar
        status = Label(self, text="Ready", bd=1, relief=SUNKEN, anchor=W)
        status.pack(side=BOTTOM, fill=X)

    #Send Button Callback Function
    def sendCoins(self):
        print('Sent {} BitCoins to reciever: {}'.format(self.amountBox.get(), self.recieverKey.get("1.0",END)))

def main():
  
    root = Tk()
    
    app = GUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
