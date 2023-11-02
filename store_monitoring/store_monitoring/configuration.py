"""
Author: Lav Sharma
Created on: 29th Oct 2023
"""

import configparser
import os

# ===================================================================
# Get the package relative's path
# ===================================================================
lstr_package_path = os.path.dirname(os.path.realpath(__file__))

# ===================================================================
# Generate the config file path
# ===================================================================
lstr_config_file_path = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + "data" + \
                        os.path.sep + "config.ini"

# ===================================================================
# Create the configparser object
# ===================================================================
lobj_config = configparser.ConfigParser()

# ===================================================================
# Read the config.ini file
# ===================================================================
lobj_config.read(lstr_config_file_path)

# ===================================================================
# Get the sections present in the config.ini
# ===================================================================
config_sections = lobj_config.sections()

# ===================================================================
# Check if the GENERAL section is present in the config.ini
# ===================================================================
if 'GENERAL' in config_sections:
    # ===================================================================
    # If present, then read all the GENERAL section variables
    # ===================================================================
    MODULE_NAME = str(lobj_config['GENERAL']['MODULE_NAME'])

    ALLOWED_METHODS = eval(lobj_config['GENERAL']['ALLOWED_METHODS'])
    ALLOW_HEADERS = eval(lobj_config['GENERAL']['ALLOW_HEADERS'])

    DEFAULT_STORE_TIMEZONE = str(lobj_config['GENERAL']['DEFAULT_STORE_TIMEZONE'])

    ORDER_FOR_READING_STORE_DETAILS = str(lobj_config['GENERAL']['ORDER_FOR_READING_STORE_DETAILS'])
    ORDER_FOR_READING_STORE_STATUS = str(lobj_config['GENERAL']['ORDER_FOR_READING_STORE_STATUS'])

# ===================================================================
# Check if the ENVIRONMENT section is present in the config.ini
# ===================================================================
if 'ENVIRONMENT' in config_sections:
    # ===================================================================
    # If present, then read all the ENVIRONMENT section variables
    # ===================================================================
    STORE_MONITORING_DAS_URL = str(lobj_config['ENVIRONMENT']['STORE_MONITORING_DAS_URL'])

    HOST_PROTOCOL = str(lobj_config['ENVIRONMENT']['HOST_PROTOCOL'])
    HOST_IP = str(lobj_config['ENVIRONMENT']['HOST_IP'])
    HOST_PORT = int(lobj_config['ENVIRONMENT']['HOST_PORT'])

    ORIGINS = eval(lobj_config['ENVIRONMENT']['ORIGINS'])
    ALLOW_CREDENTIALS = str(lobj_config['ENVIRONMENT']['ALLOW_CREDENTIALS'])
    IS_DEBUG = str(lobj_config['ENVIRONMENT']['IS_DEBUG'])

    RETRY_ATTEMPT_FOR_DAS_CONNECTION = int(lobj_config['ENVIRONMENT']['RETRY_ATTEMPT_FOR_DAS_CONNECTION'])
    WAITING_TIME_BETWEEN_RETRY_FOR_DAS_IN_MILLISECONDS = int(lobj_config['ENVIRONMENT'][
                                                                 'WAITING_TIME_BETWEEN_RETRY_FOR_DAS_IN_MILLISECONDS'])
    MAXIMUM_WAITING_TIME_FOR_RETRY_FOR_DAL_IN_MILLISECONDS = int(lobj_config['ENVIRONMENT'][
                                                                     'MAXIMUM_WAITING_TIME_FOR_RETRY_FOR_DAL_IN_MILLISECONDS'])

    OUTPUT_CSV_PATH = str(lobj_config['ENVIRONMENT']['OUTPUT_CSV_PATH'])
    LOGGING_LEVEL = str(lobj_config['ENVIRONMENT']['LOGGING_LEVEL'])
