import logging, os

def setup_logger():
    os.makedirs("src/logs", exist_ok=True)
    logging.basicConfig(
        filename="src/logs/monitor.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    return logging.getLogger("InternScope")
