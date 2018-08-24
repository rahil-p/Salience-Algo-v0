def debug_mode():                                       #forces an AssertionError to keep the driver running
    try:
        raise AssertionError('debug mode')
    except AssertionError:
        input('Press return to end the debugging session')

def continue_mode():                                    #forces the driver to keep running (keeps user logged in)
    raise AssertionError('continue mode - ignore traceback')
