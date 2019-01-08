import urllib3
import urllib
import json
import sched, time
import sys
import os
import signal


from flask import Flask, render_template


app = Flask(__name__)

urllib3.disable_warnings()
s = sched.scheduler(time.time, time.sleep)
coins = {}
sys.setrecursionlimit(2500)
coin = ""



def getMarketSummary():
    http = urllib3.PoolManager()
    r = http.request('GET', 'https://bittrex.com/api/v1.1/public/getmarketsummaries')
    
    req = json.loads(r.data.decode('utf-8'))

    return req


def formatList(data):
    localtime = time.asctime( time.localtime(time.time()) )
   

    for i in data['result']:
        baseValueList = []
        last = i['Last']
        baseCoin = i['MarketName'][:3]
        if i['MarketName'] in coins:
            baseValueList = coins[i['MarketName']]
            baseValueList.append(i['BaseVolume'])
            coins[i['MarketName']] = baseValueList
            if len(baseValueList)>4:
                if (baseValueList[0] - baseValueList[4]) > 50:
                    if i['MarketName'][:4] != 'USDT':
                        if 'XRP' not in i['MarketName']:
                            if i['OpenBuyOrders']>i['OpenSellOrders']:
                                direction = "Buying"
                            elif i['OpenBuyOrders']<i['OpenSellOrders']:
                                direction = "Selling"
                            else:
                                direction = "Neutral"
                                
                            print(i['MarketName'],'--',last,'--', baseValueList[0] - baseValueList[4],baseCoin,'--', localtime,'--', direction)


                            
                baseValueList.pop(0)
        else:
            baseValueList.append(i['BaseVolume'])
            coins[i['MarketName']] = baseValueList

def repeat():
    s.enter(29, 1, updateCoinList ,())
    s.run()

    

def updateCoinList():
    currentMarket = getMarketSummary()
    formatList(currentMarket)
    repeat()

@app.route('/')  
def main():
    print(".....................BITTREX SCANNER..................\n")
    print('Volume scanner that checks every 30 seconds for volume spikes')
    print('in the past 2 mins on Bittrex. Volume is labeled in base coin. ')
    print('Direction indicates whether there are more buy orders or sell orders during that time frame.\n')
    print('Scanning......\n')
    print('Coin    Last Trade    Volume change    Timestamp    Direction')
    print('----------------------------------------------------------------\n')
    return render_template('template.html',updateCoinList())

if __name__ == "__main__":
    app.run(debug=True)
