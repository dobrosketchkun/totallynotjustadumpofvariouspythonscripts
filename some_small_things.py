#########################
'''
Simple debug print
'''

DEBUG = True
def debug_print(*args, **kargs):
    global DEBUG
    if DEBUG:
        print(*args, **kargs)
#########################
'''
Headers
'''

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' 
                      'AppleWebKit/537.11 (KHTML, like Gecko) '
                      'Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}

#########################
'''
Rudimentary threading
'''

import concurrent.futures as futures

data = []
def main():
    pass

with futures.ThreadPoolExecutor(max_workers=1000) as executor:
    results = executor.map(main, data)

    
 #########################
'''
Flattening
'''

nested_lists = [[1, 2], [[3, 4], [5, 6], [[7, 8], [9, 10], [[11, [12, 13]]]]]]
flatten = lambda x: [y for l in x for y in flatten(l)] if type(x) is list else [x]
flatten(nested_lists)

#########################
'''
Timeit decorator
'''

def timeit(fn): 
    # *args and **kwargs are to support positional and named arguments of fn
    def get_time(*args, **kwargs): 
        start = time.time() 
        output = fn(*args, **kwargs)
        print(f"Time taken in {fn.__name__}: {time.time() - start:.7f}")
        return output  # make sure that the decorator returns the output of fn
    return get_time

#########################
'''
Print a text in a hackery way
'''

def printed(text, time =0.02):
	'''
	Make a cool typing effect
	'''
	for char in text:
		sleep(time)
		sys.stdout.write(char)
		sys.stdout.flush()

#########################
'''
Clear the screen in terminal/cmd
'''

def clear_screen():
    """
    Clears the terminal screen.
    """

    command = "cls" if platform.system().lower()=="windows" else "clear"
    os.system(command)

#########################
'''
https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
Classic even chunks list cutter
'''


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

#########################
'''
Infinitely loop throuht a list
'''
import itertools
psgr = ['░','▒','▓', '█']
for element in itertools.cycle(psgr):
    print(element)

#########################
'''
Threading?..
'''


import time
from pathlib import Path
import threading
import os
try:
	os.remove('/content/_.temp')
except:
	pass

my_file = Path("/content/_.temp")


def func1():
  counter = 0
  while not my_file.exists():
    time.sleep(1)
    print('Yet to No, ' + str(counter))
    counter += 1
  with open('temp2.txt', 'w') as file:
    file.write('Yet to No, ' + str(counter))  

def func2():
  for _ in range(10):
    time.sleep(1)
    print('This is ' + str(_))
  with open(my_file, 'w') as file:
    file.write('This is ' + str(_))

t1 = threading.Thread(target=func1)
t1.start()
t2 = threading.Thread(target=func2)
t2.start()
t2.join()


#########################
'''
To OHLC from binance tick data
'''

def ohlc_resample(dataf, length='1s'):
    dataf.index = pd.to_datetime(dataf.index, unit='ms')
    dataf.Price = pd.to_numeric(dataf.Price)
    dataf.Quantity = pd.to_numeric(dataf.Quantity)
    ticks = dataf[['Price', 'Quantity']]
    bars = ticks.Price.resample(length).ohlc()
    volumes = ticks.Quantity.resample(length).sum()
    result = pd.concat([bars, volumes], axis=1)
    result['volume'] = result['Quantity'] 
    result = result.drop(['Quantity'], axis=1)
    return result

#########################
'''
Resamle OHLC
'''

datadf = datadf.resample('1min', label='left').agg({
                                    'open': 'first',
                                    'high': 'max',
                                    'low': 'min',
                                    'close': 'last',
                                    'volume': 'sum'
                                    })
