import inspect

# Some const variable
CRED = '\033[91m'
CGREEN2 = '\33[92m'
CEND = '\033[0m'
DEBUG = 10
INFO = 20
ERROR = 30
LOGGING_LEVEL = 0


def set_debug(isset: bool):
    global LOGGING_LEVEL
    if isset:
        LOGGING_LEVEL = DEBUG
    else:
        LOGGING_LEVEL = INFO


def info(*args, level=INFO):
    if level < LOGGING_LEVEL:
        return

    prompt = ''
    if level == DEBUG:
        prompt = 'Debug'
    elif level == INFO:
        prompt = 'Info'
    elif level == ERROR:
        prompt = 'Error'
    if level in (DEBUG, ERROR):
        current_frame = inspect.currentframe()
        if current_frame is not None:
            func = inspect.getframeinfo(current_frame.f_back).function
            print(CRED + ('[%s] <%s>' % (prompt, func)) + CGREEN2, *args, CEND)
        else:
            print(CRED + ('[%s]' % prompt) + CGREEN2, *args, CEND)
    else:
        print(CRED + ('[%s]' % prompt) + CGREEN2, *args, CEND)
