# BTFGMonitor

## How to run the monitor

Run in Windows using the executable file, or with Python 2 or 3 using the Python source file.

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
currentFund = max((poolBalance + blockReward - totalPending - 3000), blockReward)
estimateActual = (currentFund/totalShare)*minerShare
```

**Current Block** - The current block that the network is on.

**Shares per Block** - Your mining share in the pool for each block in the current round.

**Total Share** - Your mining share in the pool for the current round.

## Forks

Angular 5/Electron: https://github.com/javajohnHub/BtfgMonitor
