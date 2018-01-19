#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function
import configparser
import urllib3
import requests
import sys
import os
import time
import warnings
import six

try:
   import colorama
   colorama.init()
except:
   try:
       import tendo.ansiterm
   except:
       pass

warnings.filterwarnings("ignore")

# GRAPH FUNCTIONS
def normalize(data):
    """Data normalization"""
    min_dat = min(data)
    max_dat = max(data)
    avg_dat = sum(data) / float(len(data))
    if max_dat == min_dat:
        norm_factor = 1
    else:
        norm_factor = (MAX_WIDTH / 2) / float(max_dat - min_dat)
    normal_dat = [(_v - min_dat) * norm_factor for _v in data]
    return normal_dat

def horizontal_rows(labels, data, normal_dat):
    """Generates chart rows"""
    if data:
        try:
            val_min = min(point for point in data if point > 0.0)
        except:
            val_min = 0
        val_max = max(data)
    else:
        val_min = 0
        val_max = 0
    for i in reversed(range(len(labels))):
        label = "{}: ".format(labels[i])
        value = data[i]
        num_blocks = normal_dat[i]
        tail = ' {}{}'.format('{:<7.8f}'.format(value), '')
        yield (label, value, int(num_blocks), val_min, val_max, tail)

def print_row(label, value, num_blocks, val_min, val_max, tail):
    """Prints a single chart row"""
    print(label, end="")
    if value <= 0:
        print('\x1b[1;31;40m' + "no deadline" + '\x1b[0m') 
    elif num_blocks < 1 and value > 0:
        #prints a single tick for positive data points normalized to < 1
        
        if value <= val_min:
            sys.stdout.write('\x1b[1;31;40m' + TICK + '\x1b[0m')
            print(" " + str(tail))
        else:
            sys.stdout.write('\x1b[1;33;40m' + TICK + '\x1b[0m')
            print(" " + str(tail))
    else:
        #prints 2 ticks for normalized data > 1
        if value >= val_max:
            for i in range(num_blocks):
                sys.stdout.write('\x1b[1;32;40m' + TICK+TICK +'\x1b[0m')
            print(" " + str(tail))
        else:
            for i in range(num_blocks):
                sys.stdout.write('\x1b[1;33;40m' + TICK+TICK + '\x1b[0m')
            print(" " + str(tail))

# PRINT FUNCTIONS
def print_output(blockLabels, blockShares, accountData, pendingPayment, totalShare, minerShare, totalPending):
    """Main print function"""
    #print current time
    print('\x1b[1m' + "Last Update: " + '\x1b[0m' + time.strftime("%x") + " " + time.strftime("%X"))
    #print wallet data
    print_account_data(accountData)
    #print pending payment
    print('\x1b[1m' + "Pending Balance: " + '\x1b[0m' + '\x1b[1;33;40m' + str(pendingPayment) + '\x1b[0m' + '\x1b[1;31;40m' + " BURST" + '\x1b[0m')
    #print estimated payout
    print_estimated_reward(totalShare, minerShare, totalPending)
    #print current block info
    print_cur_block()

    if (DISPLAY_SHARES == 1):
        if (len(blockShares) > 0):
            #normalize data
            normal_dat = normalize(blockShares)

            print("\n" + '\x1b[1m' + "Shares per Block (Current Round):" + '\x1b[0m')

            # Generate data for a row.
            for row in horizontal_rows(blockLabels, blockShares, normal_dat):
                print_row(*row)
            print('\x1b[1m' + "Total Share: " + '\x1b[0m' + str(format(minerShare,'.4f')) + " / " + str(format(totalShare, '.4f')))
        else:
            print("New round, no new blocks")

    for i in range(MAX_WIDTH + 20):
        sys.stdout.write('\x1b[2;34;40m' + SPACER + '\x1b[0m')
    print("")

def print_cur_block():
    """Gets and prints the current block number"""
    url = "https://wallet.burst.cryptoguru.org:8125/burst?requestType=getBlockchainStatus"
    data = requests.get(url)
    data = data.json()
    print('\x1b[1m' + "Current Block: " + '\x1b[0m' + '\x1b[1;36;40m' + str(data["numberOfBlocks"]) + '\x1b[0m')

def print_estimated_reward(totalShare, minerShare, totalPending):
    data = requests.get("https://wallet.burst.cryptoguru.org:8125/burst?requestType=getAccount&account=9146480761707329845")
    data = data.json()

    poolBalance = str(data["effectiveBalanceNXT"])
    poolBalance = poolBalance[:-8] + '.' + poolBalance[-8:]
    poolBalance = float(poolBalance)

    blockData = requests.get("https://wallet.burst.cryptoguru.org:8125/burst?requestType=getBlocks&firstIndex=1&lastIndex=1")
    blockData = blockData.json()
    blockReward = float(blockData["blocks"][0]["blockReward"])

    if totalShare == 0:
        estimateBaseline = 0
        estimateActual = 0
    else: 
        estimateBaseline = (minerShare*blockReward)/totalShare
        estimateBaseline = format(estimateBaseline, '.4f')

        currentFund = max((poolBalance + blockReward - totalPending - 3000), blockReward)
        estimateActual = (currentFund/totalShare)*minerShare
        estimateActual = format(estimateActual,'.4f')
    print('\x1b[1m' + "Estimated Baseline Revenue: " + '\x1b[0m' + "~" + str(estimateBaseline) + '\x1b[1;31;40m' + " BURST" + '\x1b[0m')
    print('\x1b[1m' + "Estimated Actual Revenue: " + '\x1b[0m' + "~" + str(estimateActual) + '\x1b[1;31;40m' + " BURST" + '\x1b[0m')


def print_account_data(data):
    """Prints user wallet data"""
    try:
        if "errorCode" in data:
            #failed burst address/ID
            print("Error: " + data["errorDescription"])
        else:
            #parse and print wallet name, address, and current balance
            currentBalance = data["balanceNQT"]
            if len(currentBalance) > 8:
                currentBalance = currentBalance[:-8] + '.' + currentBalance[-8:]
            else:
                currentBalance = "0." + currentBalance

            if "name" in data:
                print('\x1b[1m' + "Name: " + '\x1b[0m' + '\x1b[0;35;40m' + data["name"] + '\x1b[0m')
            if "description" in data:
                print('\x1b[1m' + "Description: " + '\x1b[0m' + data["description"])
            print('\x1b[1m' + "Address: " + '\x1b[0m' + data["accountRS"])
            print('\x1b[1m' + "Current Balance: " + '\x1b[0m' + '\x1b[1;32;40m' + currentBalance + '\x1b[0m' + '\x1b[1;31;40m' + " BURST" + '\x1b[0m')
    except:
        print("Error processing Account JSON data")

# JSON PROCESSING
def burst_data():
    """Main data processing"""
    data = ""
    accountData = ""
    try:
        #get pool data
        data = requests.get('http://104.128.234.137/pool-payments.json')
        data = data.json()

        #get user wallet data
        accountData = requests.get("https://wallet.burst.cryptoguru.org:8125/burst?requestType=getAccount&account=" + numeric_id)
        accountData = accountData.json()
    except:
        print("Error processing JSON data")

    #get pool pending payout
    try:
        if numeric_id in data["pendingPaymentList"]:
            pending = data["pendingPaymentList"][numeric_id]
        else:
            pending = 0
    except:
        pending = "N/A"

    totalPending = 0
    try:
        for pending_id in data["pendingPaymentList"]:
            totalPending += data["pendingPaymentList"][pending_id]
        totalPending = float(format(totalPending,'.4f'))
    except:
        totalPending = 0

    #parse pool data
    blockLabels = []
    blockShares = []
    totalShare = 0
    minerShare = 0
    try:
        for block in data["blockPaymentList"]:
            blockLabels.append(block["height"])
            totalShare += block["totalShare"]
            shareFound = 0
            for share in block["shareList"]:
                if share["accountId"] == numeric_id:
                    blockShares.append(share["share"])
                    minerShare += share["share"]
                    shareFound = 1
            if shareFound == 0:
                blockShares.append(0.0)
    except:
        print("Error, could not process blocks and shares")

    #clears screen after each round
    os.system('cls' if os.name == 'nt' else 'clear')

    #std output function (print)
    print_output(blockLabels, blockShares, accountData, pending, totalShare, minerShare, totalPending)

# UTILITY FUNCTIONS
def burst_to_numeric(numeric_id):
    """Converts a burst address into a numeric id"""  
    try:
        accountData = requests.get("https://wallet.burst.cryptoguru.org:8125/burst?requestType=getAccount&account=" + numeric_id)
        accountData = accountData.json()
        return accountData["account"]
    except:
        print("Error processing Account JSON data")

# MAIN
if __name__ == "__main__":
    #default config
    MAX_WIDTH = 40
    DISPLAY_SHARES = 1
    INTERVAL = 360

    #chart character
    TICK = b'\xe2\x96\x88'.decode('utf-8')
    SPACER = b'\xe2\x96\x84'.decode('utf-8')

    #clear screen
    os.system('cls' if os.name == 'nt' else 'clear')

    #Handle user input and config
    config = configparser.ConfigParser()    

    print('\x1b[1m' + "BTFG Monitor v1.0" + '\x1b[0m')
    print("created by " + '\x1b[0;34;46m' + "velagand\n" + '\x1b[0m')

    if not os.path.exists('BTFGMonitor.ini'):
        #if no config file
        print('\x1b[1;31;40m' + "No config found! Is this your first time running BTFG Monitor?\n" + '\x1b[0m') 

        #convert inputted burst address or numerical ID to numeric ID
        numeric_id = six.moves.input('\x1b[1m' + "Enter your BURST Address or Numeric ID: " + '\x1b[0m').strip()
        numeric_id = burst_to_numeric(numeric_id)
        
        #user config
        print('\x1b[0;31;47m' + "\nLeave the following blank for default values (hit enter):" + '\x1b[0m')
        shares_input = six.moves.input('\x1b[1m' + "Display Block Shares (default=yes): " + '\x1b[0m').strip().lower()
        interval_input = six.moves.input('\x1b[1m' + "Update Frequency (default=360, minimum=60): " + '\x1b[0m').strip()
        width_input = six.moves.input('\x1b[1m' + "Max Chart Width (default=40): " + '\x1b[0m').strip()

        #create config
        config['DEFAULT'] = {'id' : numeric_id,
                             'displayShares': shares_input,
                             'interval': interval_input,
                             'width': width_input}
        #write config file
        with open('BTFGMonitor.ini', 'w') as f:
            config.write(f)
        print('\x1b[1;32;40m' + "Config file created!" + '\x1b[0m')
    else:
        print('\x1b[1;32;40m' + "Config file found!" + '\x1b[0m')
        config.read('BTFGMonitor.ini')
        try:
            numeric_id = config['DEFAULT']['id']
            shares_input = config['DEFAULT']['displayShares']
            interval_input = config['DEFAULT']['interval']
            width_input = config['DEFAULT']['width']
        except:
            print("Error, parsing config failed")

    if shares_input == 'no' or shares_input=='n':
        DISPLAY_SHARES = 0
    if not interval_input or int(interval_input) < 60:
        pass
    else:
        INTERVAL = int(interval_input)
    if not width_input:
        pass
    else:
        MAX_WIDTH = int(width_input)

    for i in range(MAX_WIDTH + 20):
        sys.stdout.write('\x1b[2;34;40m' + SPACER + '\x1b[0m')
    print()
    
    while True:
        burst_data()
        time.sleep(INTERVAL)