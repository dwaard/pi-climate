from envparse import env
import logging

# This recurses up the directory tree until a file called '.env' is found.
env.read_envfile()

# Set the logging configuration
logging.basicConfig(
    filename=env('LOGGING_FILENAME', default=None), 
    format=env('LOGGING_FORMAT', default='%(asctime)s %(levelname)s: %(message)s'), 
    level=env('LOGGING_LEVEL', default='WARNING')
)
# disable logging
if not env.bool('LOGGING_ENABLED', default=True):
    logging.disable('CRITICAL')

def parseIntThatMightBeHex(str):
    if str.lower().startswith('0x'):
        return int(str, 16)
    return int(str)


if __name__ == '__main__':
    # Log some warning
    if env('LOGGING_LEVEL', default='WARNING') == 'WARNING':
        logging.warning("Logs warnings and more severe messages only")

    # Some example environment variable
    max_rows = env.int('MAX_ROWS', default=100)
    logging.debug("Max rows: {}".format(max_rows))
