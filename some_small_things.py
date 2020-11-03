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
