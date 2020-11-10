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
