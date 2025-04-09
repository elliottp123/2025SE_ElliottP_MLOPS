import logging
import os

def setup_logging():
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/debug.log'),
            logging.StreamHandler()
        ]
    )

    # Create logger
    logger = logging.getLogger('prediction_app')
    logger.setLevel(logging.DEBUG)

    return logger