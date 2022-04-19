import discord
import requests
import json
from web3 import Web3
import asyncio, time
import csv



bsc = "https://bsc-dataseed.binance.org/"
web3 = Web3(Web3.HTTPProvider(bsc))
print("connection au réseau : "+str(web3.isConnected()))
TokenAddress = "0xE5bA47fD94CB645ba4119222e34fB33F59C7CD90"
url_eth = "https://api.bscscan.com/api"
contract_address = web3.toChecksumAddress(TokenAddress)
API_ENDPOINT = url_eth+"?module=contract&action=getabi&address="+str(contract_address)
r = requests.get(url = API_ENDPOINT)
response = r.json()
abi=json.loads(response["result"])
client = discord.Client()

contract = web3.eth.contract(address=contract_address, abi=abi)
totalSupply = contract.functions.totalSupply().call()
#print(totalSupply)
#print(contract.functions.name().call())
#print(contract.functions.symbol().call())
class wallet:
    address = ""
    invest  = 0
    balance = 0
    users = {}
    def __init__(self, address, invest, users):
        self.address = address
        self.invest = invest
        self.users = users


showGain = 0
fiat = "USD"
symbFiat = "$"
previousBalance = 0
API_CMC = "<YOUR_COINMARKETCAP_API>"

async def append_new_line(file_name, text_to_append):
    """Append given text as a new line at the end of file"""
    # Open the file in append & read mode ('a+')
    with open(file_name, "a+") as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        # Append text at the end of file
        file_object.write(text_to_append)
    
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    walletAddr = input("Please enter the wallet address : ")
    walletInvestissement = input("Please enter the ammount deposited in the wallet in safuu : ")
    walletUsersnames = input("Please enter the wallet usersname separated by a comma : ")
    print("you entered : "+walletUsersnames)
    walletUsersnames = walletUsersnames.split(",")
    walletUsersParts = input("Please enter the % owned by each users separated by a comma (in the same order than entered previously): ")
    walletUsers = {}
    walletUsersParts = walletUsersParts.split(",")
    walletUsersBalances = {}
    for x in range(len(walletUsersParts)):
        walletUsersBalances[x] = round((float(walletInvestissement)/100)*float(walletUsersParts[x]),5)
    for i in range(len(walletUsersnames)):
        walletUsers[i] = {"name":walletUsersnames[i],"part":walletUsersParts[i],"balance":walletUsersBalances[i]}
    global walletObj
    walletObj = wallet(walletAddr,walletInvestissement,walletUsers)
    client.loop.create_task(refreshStatus())


async def get_price():
    global fiat
    r = requests.get("https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest?CMC_PRO_API_KEY="+API_CMC+"&convert="+fiat)
    #print(r.status_code)
    json_data = json.loads(r.text)
    prix = json_data["data"]["18515"]["quote"][fiat]["price"]
    return prix


async def get_balance():
    global walletObj
    address = web3.toChecksumAddress(walletObj.address)
    weiBalance = contract.functions.balanceOf(address).call()
    balance = weiBalance / 10**5
    global previousBalance
    if(balance > previousBalance):
        await append_new_line("./walletTrack.txt", str(balance))
        previousBalance = balance
    walletObj.balance = balance
    for i in range(len(walletObj.users)):
        walletObj.users[i]["balance"] = round((balance/100)*float(walletObj.users[i]["part"]),2)
    return balance
    
async def refreshStatus(): 
    global showGain
    global walletObj
    while True:
        prix = await get_price()
        balance = await get_balance()
        valEuro = round(float(prix) * float(balance),2)
        #discord.Activity(name="Test", type=5)
        if(showGain == 0):
            balance = round(float(balance),5)
            await client.user.edit(nick=str(balance)+" ⛨ ")
            print("nickname changed to : "+str(balance)+" ⛨ ")
            await client.change_presence(activity=discord.Game(name=str(balance)+" ⛨|"+str(valEuro)+symbFiat, url="https://coinmarketcap.com/fr/currencies/safuu/"))
        else :
            gain = balance-walletObj.invest
            gain = round(float(gain),5)
            valEuro = round(float(prix) * float(gain),2)
            await client.user.edit(nick=str(gain)+" ⛨ ")
            print("nickname changed to : "+str(gain)+" ⛨ ")
            await client.change_presence(activity=discord.Game(name=str(gain)+" ⛨|"+str(valEuro)+symbFiat, url="https://coinmarketcap.com/fr/currencies/safuu/"))

        await asyncio.sleep(900)


async def refreshStatusNoLoop(): 
    global showGain
    global walletObj

    prix = await get_price()
    balance = await get_balance()
    valEuro = round(float(prix) * float(balance),2)
    if(showGain == 0):
        balance = round(float(balance),5)
        await client.change_presence(activity=discord.Game(name=str(balance)+" ⛨|"+str(valEuro)+symbFiat, url="https://coinmarketcap.com/fr/currencies/safuu/"))
    else :
        gain = balance-walletObj.invest
        gain = round(float(gain),5)
        valEuro = round(float(prix) * float(gain),2)
        await client.change_presence(activity=discord.Game(name=str(gain)+" ⛨|"+str(valEuro)+symbFiat, url="https://coinmarketcap.com/fr/currencies/safuu/"))

async def getUserBalanceFromName(name):
    global walletObj
    currBalance = await get_balance()
    for i in range(len(walletObj.users)):
        if(walletObj.users[i]["name"] == name):
            currPartUser = float(walletObj.users[i]["part"])
            currBalanceUser = round((currBalance/100)*currPartUser,2)
            return currBalanceUser
    return 0

async def calcPart(amtTotal,amtUser):
    amtTotal = float(amtTotal)
    amtUser = float(amtUser)
    part = round((amtUser/amtTotal)*100,2)
    return part


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    global symbFiat
    global walletObj

    if (message.content.lower().startswith('$rich')):
        currBalance = await get_balance()
        currPrice = await get_price()
        currValEuro = round(float(currPrice) * float(currBalance),2)
        await message.channel.send("You have "+str(currBalance)+" ⛨ | "+str(currValEuro)+symbFiat)
        for i in range(len(walletObj.users)):
            currUser = walletObj.users[i]
            currUserPart = currUser["part"]
            currUserBalance = round((currBalance/100)*float(currUserPart),5)
            currUserValEuro = round(float(currPrice) * float(currUserBalance),2)
            await message.channel.send(currUser["name"]+" : "+str(currUserBalance)+" ⛨ | "+str(currUserValEuro)+" "+symbFiat)
    
    if message.content.lower().startswith('$retire'):
        name = message.content.split(" ")[1]
        amt = message.content.split(" ")[2]
        print("name : "+name+" amt : "+amt)
        balanceGlobal = await get_balance()
        #Remove the safuu from the wallet and calculate part of users
        for x in walletObj.users:
            currUser = walletObj.users[x]
            if currUser['name'] == name:
                balanceUser = currUser["balance"]
                if(float(amt) > float(balanceUser)):
                    await message.channel.send("You don't have enough money to retire "+str(amt)+" ⛨ for "+name)
                else:
                    walletObj.users[x]["balance"] = balanceUser - float(amt)
                    balanceGlobal = walletObj.balance
                    currUser["part"] = await calcPart(balanceGlobal,balanceUser)
                    await message.channel.send("You have withdrawn "+str(amt)+" ⛨ for "+name)
                    await message.channel.send("The datas can only get correct if you effectively retire "+str(amt)+" ⛨ from your wallet")
                break
        balanceGlobal = walletObj.balance - float(amt)
        for i in range(len(walletObj.users)):
            currUser = walletObj.users[i]
            balanceUser = currUser["balance"]
            currUser["part"] = await calcPart(balanceGlobal,balanceUser)
            await message.channel.send(currUser["name"]+" : "+str(currUser["part"])+"%")
        

        
        

    if message.content.lower().startswith('$add'):
        name = message.content.split(" ")[1]
        amt = message.content.split(" ")[2]
        print("name : "+name+" amt : "+amt)
        balanceGlobal = await get_balance()
        for x in walletObj.users:
            currUser = walletObj.users[x]
            if currUser['name'] == name:
                balanceUser = currUser["balance"]
                walletObj.users[x]["balance"] = balanceUser + float(amt)
                balanceGlobal = walletObj.balance
                currUser["part"] = await calcPart(balanceGlobal,balanceUser)
                await message.channel.send("You have added "+str(amt)+" ⛨ for "+name)
                await message.channel.send("The datas can only get correct if you effectively add "+str(amt)+" ⛨ to your wallet")
                break
        balanceGlobal = walletObj.balance + float(amt)
        for i in range(len(walletObj.users)):
            currUser = walletObj.users[i]
            balanceUser = currUser["balance"]
            currUser["part"] = await calcPart(balanceGlobal,balanceUser)
            await message.channel.send(currUser["name"]+" : "+str(currUser["part"])+"%")

    if message.content.lower().startswith('$parts'):
        for i in range(len(walletObj.users)):
            currUser = walletObj.users[i]
            await message.channel.send(currUser["name"]+" : "+str(currUser["part"])+"%")
            
    if message.content.lower().startswith('$refresh'):
        await refreshStatusNoLoop()
        await message.channel.send("Datas had been refreshed")

    if message.content.lower().startswith('$fiat'):
        global fiat
        oldFiat = fiat
        fiat = message.content.split(' ')[1].upper()
        if(fiat == "EUR"):
            symbFiat = "€"
        elif(fiat == "USD"):
            symbFiat = "$"
        elif(fiat == "GBP"):
            symbFiat = "£"
        elif(fiat == "JPY"):
            symbFiat = "¥"
        elif(fiat == "CAD"):
            symbFiat = "$"
        elif(fiat == "AUD"):
            symbFiat = "$"
        elif(fiat == "CHF"):
            symbFiat = "Fr"
        elif(fiat == "CNY"):
            symbFiat = "¥"
        elif(fiat == "SEK"):
            symbFiat = "kr"
        elif(fiat == "NZD"):
            symbFiat = "$"
        await refreshStatusNoLoop()
        await message.channel.send("Fiat changed from "+str(oldFiat)+" to "+str(fiat))

    if (message.content.lower().startswith('$gain') ):
        global showGain
        if(showGain == 0):
            showGain = 1
            await refreshStatusNoLoop()
            await message.channel.send("Showing the gain")
        else:
            showGain = 0
            await refreshStatusNoLoop()
            await message.channel.send("Showing the global value")

    if (message.content.lower().startswith('$help') or message.content.lower().startswith('$?')):
        await message.channel.send("$rich : show your current balance\n$retire <name> <amount> : withdraw money from your wallet\n$add <name> <amount> : add money to your wallet\n$parts : show the part of each user\n$refresh : refresh the datas\n$fiat <fiat> : change the fiat\n$gain : show the gain of the wallet in status")

client.run('<YOUR_DISCORD_TOKEN>')
