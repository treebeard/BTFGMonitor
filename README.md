# BTFGMonitor

<p align="center">
  <img src="https://github.com/treebeard/BTFGMonitor/raw/master/screenshot.png" alt="Screenshot"></img>  
</p>

## How to run the monitor

Run in Windows using the executable file (found under 'releases'), or with Python 2 or 3 using the Python source file.

1. When prompted, enter either your BURST Address (BURST-XXXX-XXXX-XXXX-XXXXX) or Numeric ID and hit enter
2. Display Block Shares - Displays a graph of your shares (default: **yes**)
3. Update Frequency - Time in seconds between monitor updates (default: **360**, minimum: **60**)
4. Max Chart Width - Max character width of the graph's bars (default: **40**)
5. Currency - Displays fiat currency values (default: **USD**, options: **AUD**, **BRL**, **CAD**, **CHF**, **CLP**, **CNY**, **CZK**, **DKK**, **EUR**, **GBP**, **HKD**, **HUF**, **IDR**, **ILS**, **INR**, **JPY**, **KRW**, **MXN**, **MYR**, **NOK**, **NZD**, **PHP**, **PKR**, **PLN**, **RUB**, **SEK**, **SGD**, **THB**, **TRY**, **TWD**, **USD**, **ZAR**) 
6. A config file (BTFGMonitor.ini) will be saved in the same location as the application. Open and modify this file with a text editor to change the configuation.

## How to interpret the monitor

**Current Balance** - Your wallet's current confirmed balance.

**Pending Balance** - Your pool earnings which have not yet hit the minimum payout.

**Estimated Baseline Revenue** - Your estimated earnings if the pool were to win the current block (uses only block reward in calculation).

```python
estimateBaseline = (minerShare*blockReward)/totalShare
```

**Estimated Actual Revenue** - Your estimated earnings if the pool were to win the current block (uses both pool balance and block reward in calculation).

```python
currentFund = blockReward + ((poolBalance - totalPending)*.1)
estimateActual = (currentFund/totalShare)*minerShare
```

**Current Block** - The current block that the network is on.

**Shares per Block** - Your mining share in the pool for each block in the current round.

**Total Share** - Your mining share in the pool for the current round.

**Payment Deferred** - BTFG pool does not pay based off of block reward. It pays based on the pool balance and the amount pending in order to ensure that 100% of the funds, including dust accumulation, is paid back to miners. It is also how we distribute the dividends, from the BTFG asset that the pool earns, back to miners. However, this may cause an issue during multiple quick block finds: That is, miners as a whole may end up getting paid more than they should. "Payment Deferred" is the pool's way of equalizing the books. You will still make the same for that block, but you would have recieved a partial advance from that multiple block find. Your shares are kept past the next block find and will be applied to the win after that.

## Forks

Angular 5/Electron: https://github.com/javajohnHub/BtfgMonitor
