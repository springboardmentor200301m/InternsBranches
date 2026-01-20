import logging

logging.basicConfig(filename="audit.log", level=logging.INFO)

def log_access(user, query, result_count):
    logging.info(f"{user} | {query} | results={result_count}")
