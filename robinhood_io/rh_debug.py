def debug_mode():                                       #forces an AssertionError to keep the driver running
    try:
        raise AssertionError('debug mode')
    except AssertionError:
        input('Press return to end the debugging session')

def force_error():                                      #forces the driver to keep running after the script ends
    raise AssertionError('continue mode - ignore traceback')
