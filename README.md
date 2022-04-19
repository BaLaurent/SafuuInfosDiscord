# SafuuInfosDiscord
A discord bot made in python to help manage a multi-user wallet

# In this project i'll use ⛨ as the symbol for SAFUU

# Features 
Manage multiple users sharing 1 wallet
Automaticaly recalculate ratio owned on withdraw / add of safuu

![Capture d’écran 2022-04-20 000236](https://user-images.githubusercontent.com/27644308/164109552-22d3f340-929a-4fbc-b137-e101035aea0e.png)
Display infos in status : 
  can either display global wallet value :
  
  ![Capture d’écran 2022-04-20 000300](https://user-images.githubusercontent.com/27644308/164109650-4efca628-7efe-46b6-9ce0-13d02d76ecdc.png)
  
  or the benefits related to invested amount : 
  
   ![Capture d’écran 2022-04-20 000320](https://user-images.githubusercontent.com/27644308/164109715-2395b5d9-582d-4d7f-8e2c-16e9c7fa5d70.png)



# HOW TO SETUP 

This guide will assume you have python and pip installed if you don't, please install it

run this to install requirements :
```
pip install discord
pip install requests
pip install json
pip install web3
pip install asyncio
```

you'll need a discord bot account, the required scope is **bot** permissions are **Send Messages**,**Change Nickname**
follow this steps https://discordpy.readthedocs.io/en/stable/discord.html then once the bot account is created come back

you will also need a coinmarketcap api key, https://coinmarketcap.com/api/

Once the bot account created get his token (it can be found on the **"Bot"** page of discord dev's interface)

open **main.py** and replace <YOUR_DISCORD_TOKEN> by your discord token

in **main.py** replace <YOUR_COINMARKETCAP_API> by your coinmarketcap api key

open an Command Line Interface in the folder where main.py is located

in that CLI type `python3 main.py`

then follow the instructions

if you have any problem please open an issue

if you want to do any tips you can to this address : **0x0d004dc793b724490B192002cD76Ec0Cf43AD87C**

# COMMANDS
 
$help : show commands

$rich : show your current balance

$retire <name> <amount> : withdraw money from your wallet
 
$add <name> <amount> : add money to your wallet
 
$parts : show the part of each user
 
$refresh : refresh the datas
 
$fiat <fiat> : change the fiat
 
$gain : show the gain of the wallet in status
