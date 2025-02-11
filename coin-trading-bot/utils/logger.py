import logging

logging.basicConfig(level=logging.INFO)

def log_message(message):
    """Logs a message."""
    logging.info(message)

if __name__ == "__main__":
    log_message("This is a test log entry.")
