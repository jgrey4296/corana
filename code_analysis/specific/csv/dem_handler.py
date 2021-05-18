#!/usr/bin/env python3
import logging as root_logger
logging = root_logger.getLogger(__name__)


def handle_democracy(data, rows):

    filename = data.source_file

    if 'simulation' in filename:
        data.flag('simulation')
    elif 'policies' in filename:
        data.flag('policy')
    elif 'votertypes' in filename:
        data.flag('voter')
    elif:
        logging.info("Secondary Democracy Data, skipping for now")
        data.flag('discard')

def handle_simulation(data, rows):
    pass
def handle_policies(data, rows):
    pass
def handle_voters(data, rows):
    pass
