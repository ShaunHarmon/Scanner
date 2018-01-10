import urllib
import urllib3
import json
import sched, time
import sys
from tkinter import *
import tkinter as ttk

 
root = Tk()
root.title("Volume Selector")
 
# Add a grid
mainframe = Frame(root)
mainframe.grid(column=0,row=0, sticky=(N,W,E,S) )
mainframe.columnconfigure(0, weight = 1)
mainframe.rowconfigure(0, weight = 1)
mainframe.pack(pady = 100, padx = 100)
 
# Create a Tkinter variable
tkvar = StringVar(root)
 
# Dictionary with options
choices = [ '25','75','50','100','150']

 
popupMenu = OptionMenu(mainframe, tkvar, *choices)
Label(mainframe, text="Choose volume trigger").grid(row = 1, column = 1)
popupMenu.grid(row = 2, column =1)
tkvar.set('50') # set the default option

urllib3.disable_warnings()
s = sched.scheduler(time.time, time.sleep)
coins = {}
sys.setrecursionlimit(2500)




def getMarketSummary():
    http = urllib3.PoolManager()
    r = http.request('GET', 'https://bittrex.com/api/v1.1/public/getmarketsummaries')
    
    req = json.loads(r.data.decode('utf-8'))

    return req


def formatList(data):
    localtime = time.asctime( time.localtime(time.time()) )
   
    volume = (tkvar.get())
 
    for i in data['result']:
        baseValueList = []
        last = i['Last']
        baseCoin = i['MarketName'][:3]
        if i['MarketName'] in coins:
            baseValueList = coins[i['MarketName']]
            baseValueList.append(i['BaseVolume'])
            coins[i['MarketName']] = baseValueList
            if len(baseValueList)>4:
                if (baseValueList[0] - baseValueList[4]) > float(volume):
                    if i['MarketName'][:4] != 'USDT':
                        if 'XRP' not in i['MarketName']:
                            if i['OpenBuyOrders']>i['OpenSellOrders']:
                                direction = "Buying"
                            elif i['OpenBuyOrders']<i['OpenSellOrders']:
                                direction = "Selling"
                            else:
                                direction = "Neutral"
                                
                            print(i['MarketName'],'--',float('{0:.15f}'.format(last)),'--', baseValueList[0] - baseValueList[4],baseCoin,'--', localtime,'--', direction)
                        
                            
                baseValueList.pop(0)
        else:
            baseValueList.append(i['BaseVolume'])
            coins[i['MarketName']] = baseValueList



    

def updateCoinList():
    currentMarket = getMarketSummary()
    formatList(currentMarket)
    s.enter(30, 1, updateCoinList ,())
    s.run()

    
def main():
    print(".....................BITTREX SCANNER..................\n")
    print('Volume scanner that checks every 30 seconds for volume spikes')
    print('in the past 2 mins on Bittrex. Volume is labeled in base coin. ')
    print('Direction indicates whether there are more buy orders or sell orders during that time frame.\n')
    root.mainloop()
    print('Scanning......\n')
    print('Coin    Last Trade    Volume change    Timestamp    Direction')
    print('----------------------------------------------------------------\n')
    updateCoinList()

if __name__ == "__main__":
    main()
    
