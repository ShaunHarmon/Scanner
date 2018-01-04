import urllib
import urllib3
import json
import sched, time
import sys

urllib3.disable_warnings()
s = sched.scheduler(time.time, time.sleep)
coins = {}
MAXSIZE = 10
sys.setrecursionlimit(2500)




def getMarketSummary():
    http = urllib3.PoolManager()
    r = http.request('GET', 'https://bittrex.com/api/v1.1/public/getmarketsummaries')
    
    req = json.loads(r.data.decode('utf-8'))

    return req


def formatList(data):
    localtime = time.asctime( time.localtime(time.time()) )
    
    for i in data['result']:
        baseValueList = []
        if i['MarketName'] in coins:
            baseValueList = coins[i['MarketName']]

            #do logic to filter array here
            baseValueList.append(i['BaseVolume'])
            coins[i['MarketName']] = baseValueList
            if len(baseValueList)>4:
                if (baseValueList[0] - baseValueList[4]) > 50:
                    if i['MarketName'][:4] != 'USDT':
                        print(i['MarketName'],i['Last'], baseValueList[0] - baseValueList[4], localtime)
                    
                        
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
    print('Running......')
    updateCoinList()

if __name__ == "__main__":
    main()

