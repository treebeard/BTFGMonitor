#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function
import configparser
import urllib3
import requests
import sys
import os
import threading
import time
import warnings
import six

try:
	import tendo.ansiterm
except:
	try:
	   	import colorama
		colorama.init()
	except:
	   pass

try:
	session = requests.Session()
	adapter = requests.adapters.HTTPAdapter(max_retries=5)
	session.mount('https://', adapter)
	session.mount('http://', adapter)
except:
	print("Error: Session creation failed, please restart the monitor")
	sys.exit()

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
		tail = ' {}{}'.format('{:.0f}'.format(value), '')
		yield (label, value, int(num_blocks), val_min, val_max, tail)

def print_row(label, value, num_blocks, val_min, val_max, tail):
	"""Prints a single chart row"""
	print(label, end="")
	if value <= 0:
		print('\x1b[1;31;40m' + "no deadline" + '\x1b[0m') 
	elif num_blocks < 1 and value > 0:
		#prints a single tick for positive data points normalized to < 1
		
		if value <= val_min:
			sys.stdout.write('\x1b[1;32;40m' + TICK + '\x1b[0m')
			print(" " + str(tail) + "s")
		else:
			sys.stdout.write('\x1b[1;33;40m' + TICK + '\x1b[0m')
			print(" " + str(tail) + "s")
	else:
		#prints 2 ticks for normalized data > 1
		if value >= val_max:
			for i in range(num_blocks):
				sys.stdout.write('\x1b[1;31;40m' + TICK+TICK +'\x1b[0m')
			print(" " + str(tail) + "s")
		else:
			for i in range(num_blocks):
				sys.stdout.write('\x1b[1;33;40m' + TICK+TICK + '\x1b[0m')
			print(" " + str(tail) + "s")

# PRINT FUNCTIONS
def print_output(data, accountData):
	"""Main print function"""
	#print current time
	print('\x1b[1m' + "Last Update: " + '\x1b[0m' + time.strftime("%x") + " " + time.strftime("%X"))
	#print wallet data
	if "Name" in data["Account"]:
		print('\x1b[1m' + "Name: " + '\x1b[0m' + '\x1b[0;35;40m' + data["Account"]["Name"] + '\x1b[0m')
	if "Description" in data["Account"]:
		print('\x1b[1m' + "Description: " + '\x1b[0m' + data["Account"]["Description"])
	if "Address" in data["Account"]:
		print('\x1b[1m' + "Address: " + '\x1b[0m' + data["Account"]["Address"])
	if "Threshold" in data["Burst"] and data["Burst"]["Threshold"] == "20 Plus Weekly":
		print('\x1b[1m' + "Minimum Payout: " + '\x1b[0m' + data["Burst"]["Threshold"] + '\x1b[1;31;40m' + " BURST" + '\x1b[0m' + fiatConversion(20))
	elif "Threshold" in data["Burst"]:
		print('\x1b[1m' + "Minimum Payout: " + '\x1b[0m' + data["Burst"]["Threshold"] + '\x1b[1;31;40m' + " BURST" + '\x1b[0m' + fiatConversion(data["Burst"]["Threshold"]))
	
	print_current_balance(accountData)

	#print pending payment
	if "Pending" in data["Burst"]:
		print('\x1b[1m' + "Pending Balance: " + '\x1b[0m' + '\x1b[1;33;40m' + str(data["Burst"]["Pending"]) + '\x1b[0m' + '\x1b[1;31;40m' + " BURST" + '\x1b[0m' + fiatConversion(data["Burst"]["Pending"]))
	#print estimated payout
	if "Estimate" in data["Burst"]:
		print('\x1b[1m' + "Estimated Revenue: " + '\x1b[0m' + "~" + str(data["Burst"]["Estimate"]) + '\x1b[1;31;40m' + " BURST" + '\x1b[0m' + fiatConversion(data["Burst"]["Estimate"]))
	#print current block info
	print_cur_block()


	blockLabels = []
	blockShares = []
	try:
		for blockNum in sorted(data["Deadlines"]["Deadlines"].keys()):
			blockLabels.append(blockNum)
			blockShares.append(int(data["Deadlines"]["Deadlines"][blockNum]))
	except:
		pass

	if (DISPLAY_SHARES == 1):
		if (len(blockShares) > 0):
			#normalize data
			normal_dat = normalize(blockShares)

			print("\n" + '\x1b[1m' + "Deadlines per Block (Last 10 Blocks):" + '\x1b[0m')
			if all (key in data["Deadlines"] for key in ("Best","Average", "Worst")):
				print('\x1b[1;32;40m' + "Best: " + '\x1b[0m' + str(data["Deadlines"]["Best"]) + "s")
				print('\x1b[1;33;40m' + "Average: " + '\x1b[0m' + str(data["Deadlines"]["Average"]) + "s")
				print('\x1b[1;31;40m' + "Worst: " + '\x1b[0m' + str(data["Deadlines"]["Worst"]) + "s")

			# Generate data for a row.
			for row in horizontal_rows(blockLabels, blockShares, normal_dat):
				print_row(*row)
			if all (key in data["Shares"] for key in ("AvgDiff","PoolDiff", "Percent")):
				print('\x1b[1m' + "Historical Share: " + '\x1b[0m' + str(data["Shares"]["AvgDiff"]) + " / " + str(data["Shares"]["PoolDiff"]) + " (" + str(round(data["Shares"]["Percent"]*100,3)) + "%)")
		else:
			print("New round, no new blocks")

	for i in range(MAX_WIDTH + 20):
		sys.stdout.write('\x1b[2;34;40m' + SPACER + '\x1b[0m')
	print("")

def print_current_balance(data):
	"""Prints user wallet balance"""
	try:
		if "errorCode" in data:
			#failed burst address/ID
			print("Error: " + data["errorDescription"])
		else:
			try:
				currentBalance = data["balanceNQT"]
				balanceDigits = len(currentBalance)
				if balanceDigits > 8:
					currentBalance = currentBalance[:-8] + '.' + currentBalance[-8:]
				else:
					tempCurrent = currentBalance
					currentBalance = "0." 
					for i in range(8-balanceDigits):
						currentBalance = currentBalance + "0" 
					currentBalance = currentBalance + tempCurrent
			except:
				currentBalance = "N/A"

			print('\x1b[1m' + "Current Balance: " + '\x1b[0m' + '\x1b[1;32;40m' + currentBalance + '\x1b[0m' + '\x1b[1;31;40m' + " BURST" + '\x1b[0m' + fiatConversion(currentBalance))
	except:
		print("Error: Printing current wallet balance failed")
		pass

def print_cur_block():
	"""Gets and prints the current block number"""
	url = "https://wallet.burst.cryptoguru.org:8125/burst?requestType=getBlockchainStatus"
	data = session.get(url)
	data = data.json()
	print('\x1b[1m' + "Current Block: " + '\x1b[0m' + '\x1b[1;36;40m' + str(data["numberOfBlocks"]) + '\x1b[0m')

# UTILITY FUNCTIONS
def burst_to_numeric(address):
	"""Converts a burst address into a numeric id"""  
	try:
		accountData = session.get("https://wallet.burst.cryptoguru.org:8125/burst?requestType=getAccount&account=" + address)
		accountData = accountData.json()
		return accountData["account"]
	except:
		print("Error: Converting Burst Address to numeric id failed")

def fiatConversion(burstAmt):
	fiatVal = 0
	data = session.get('https://api.coinmarketcap.com/v1/ticker/burst/?convert=' + CURRENCY)
	data = data.json()
	data = data[0]
	in_string = "price_" + CURRENCY.lower()
	if burstAmt == "N/A":
		return ""
	else:
		if in_string in data:
			fiatVal = float(data[in_string])*float(burstAmt)
			fiatVal = '{:0.2f}'.format(fiatVal)
			return " (" + fiatVal + " " + CURRENCY.upper() + ")"
		else:
			fiatVal = float(data["price_usd"])*float(burstAmt)
			fiatVal = '{:0.2f}'.format(fiatVal)
			return " (" + fiatVal + " USD" + ")"

# JSON PROCESSING
def burst_data():
	"""Main data processing"""
	data = ""
	accountData = ""
	try:
		#get pool data
		data = session.get('http://burst.btfg.space:8000/btfgmonitor.php?api=' + API_KEY + '&id=' + numeric_id)
		data = data.json()

		#get user wallet data
		accountData = session.get("https://wallet.burst.cryptoguru.org:8125/burst?requestType=getAccount&account=" + numeric_id)
		accountData = accountData.json()
	except:
		print("Error: Processing JSON data failed")

	#clears screen after each round
	os.system('cls' if os.name == 'nt' else 'clear')

	#std output function (print)
	print_output(data, accountData)

# MAIN
if __name__ == "__main__":
	#default config
	MAX_WIDTH = 40
	DISPLAY_SHARES = 1
	INTERVAL = 300
	CURRENCY = "USD"
	API_KEY = "" #Enter BTFG API Key here

	#chart character
	TICK = b'\xe2\x96\x88'.decode('utf-8')
	SPACER = "_"

	#clear screen
	os.system('cls' if os.name == 'nt' else 'clear')

	#Handle user input and config
	config = configparser.ConfigParser()    

	print('\x1b[1m' + "BTFG Monitor v2.0" + '\x1b[0m')
	print("created by " + '\x1b[0;34;46m' + "treebeard\n" + '\x1b[0m')

	if not os.path.exists('BTFGMonitor.ini'):
		#if no config file
		print('\x1b[1;31;40m' + "No config found! Is this your first time running BTFG Monitor?\n" + '\x1b[0m') 

		#convert inputted burst address or numerical ID to numeric ID
		numeric_id = six.moves.input('\x1b[1m' + "Enter your BURST Address or Numeric ID: " + '\x1b[0m').strip()
		numeric_id = burst_to_numeric(numeric_id)
		
		#user config
		print('\x1b[0;31;47m' + "\nLeave the following blank for default values (hit enter):" + '\x1b[0m')
		shares_input = six.moves.input('\x1b[1m' + "Display Block Shares (default=yes): " + '\x1b[0m').strip().lower()
		interval_input = six.moves.input('\x1b[1m' + "Update Frequency (default=300, minimum=300): " + '\x1b[0m').strip()
		width_input = six.moves.input('\x1b[1m' + "Max Chart Width (default=40): " + '\x1b[0m').strip()
		currency_input = six.moves.input('\x1b[1m' + "Currency (default=USD): " + '\x1b[0m').strip()

		#create config
		config['DEFAULT'] = {'id' : numeric_id,
							 'displayShares': shares_input,
							 'interval': interval_input,
							 'width': width_input,
							 'currency': currency_input}
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
			currency_input = config['DEFAULT']['currency']
		except:
			print("Error: Parsing config failed, please verify config file")

	if shares_input == 'no' or shares_input=='n':
		DISPLAY_SHARES = 0

	if not interval_input or int(interval_input) < 300:
		pass
	else:
		INTERVAL = int(interval_input)

	if not width_input:
		pass
	else:
		MAX_WIDTH = int(width_input)

	if not currency_input:
		pass
	else:
		CURRENCY = str(currency_input).upper()

	for i in range(MAX_WIDTH + 20):
		sys.stdout.write('\x1b[2;34;40m' + SPACER + '\x1b[0m')
	print()

	while True:
		burst_data()
		time.sleep(INTERVAL)
