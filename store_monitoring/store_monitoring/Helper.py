import csv
from datetime import timedelta
from timeit import default_timer as timer

import pandas
import pytz

import store_monitoring.configuration as config
from store_monitoring.DASHelper import read_unique_stores, read_store_timezone, read_store_status, read_store_details
from store_monitoring.ModuleLogger import setup_logger

logger = setup_logger()


# Decorator function for time consumption of methods
def time_it(func):
    def run(*args, **kwargs):
        # start timer
        start_time = timer()

        # runs the function passes as input to decorator function
        result = func(*args, **kwargs)

        # end timer
        end_time = timer()

        # calculate time consumed
        time_taken = end_time - start_time

        # round up time
        round_time = round(time_taken, 2)

        # add log info
        logger.debug(f"Time Taken By Module {func.__name__}: " + str(round_time))

        # return results
        return result

    # call run  function
    return run


def get_day_of_week(timestamp):
    try:
        return timestamp.weekday()

    except Exception:
        raise


def calculate_time_difference(time_one, time_two):
    try:
        # ====================================================================
        # Calculate the time difference in seconds
        # ====================================================================
        time1_seconds = time_one.hour * 3600 + time_one.minute * 60 + time_one.second
        time2_seconds = time_two.hour * 3600 + time_two.minute * 60 + time_two.second

        if time1_seconds > time2_seconds:
            difference_seconds = time1_seconds - time2_seconds

        else:
            difference_seconds = time2_seconds - time1_seconds

        return difference_seconds

    except Exception:
        raise


def convert_timestamp_utc_to_local_timezone(store_status_df: pandas.DataFrame,
                                            store_timezone: str) -> pandas.DataFrame:
    try:
        # ====================================================================
        # Convert the TimestampUTC column to datetime objects and set the timezone to UTC
        # ====================================================================
        store_status_df['SS_TimestampUtc'] = pandas.to_datetime(store_status_df['SS_TimestampUtc'], utc=True)

        # ====================================================================
        # Convert the time in store_status_df from UTC to store_timezone
        # ====================================================================
        target_timezone = pytz.timezone(store_timezone)

        # ====================================================================
        # tz_localize(None) for removing -05:00 from the dataframe
        # ====================================================================
        store_status_df['SS_LocalTimestamp'] = store_status_df['SS_TimestampUtc']. \
            dt.tz_convert(target_timezone).dt.tz_localize(None)

        return store_status_df

    except Exception:
        raise


def identify_day_for_timezone(store_status_df: pandas.DataFrame) -> pandas.DataFrame:
    try:
        # ====================================================================
        # Identify the Day for every row using the SS_LocalTimestamp
        # ====================================================================
        store_status_df['SS_Day'] = store_status_df['SS_LocalTimestamp'].apply(get_day_of_week)
        return store_status_df

    except Exception:
        raise


def read_unique_stores_wrapper() -> list:
    try:
        unique_store = []

        # ====================================================================
        # Retrieve the unique StoreId's from StoreStatus table
        # ====================================================================
        unique_stores = read_unique_stores()

        if 'HttpResponseCode' in unique_stores and unique_stores['HttpResponseCode'] == 200:
            if 'ResponseCode' in unique_stores and unique_stores['ResponseCode'] == 2001:
                if 'StoreId' in unique_stores:
                    unique_store = unique_stores['StoreId']

        return unique_store

    except Exception:
        raise

    finally:
        del unique_stores


def read_store_timezone_wrapper(store_id: str) -> str:
    try:
        # ====================================================================
        # Retrieve the StoreTimezone for the store_id
        # ====================================================================
        store_timezone = read_store_timezone(store_id)

        if 'HttpResponseCode' in store_timezone and store_timezone['HttpResponseCode'] == 200:
            if 'ResponseCode' in store_timezone:
                if store_timezone['ResponseCode'] == 3003:
                    # ====================================================================
                    # Record not found in StoreTimezone table, consider default timezone
                    # ====================================================================
                    store_timezone = config.DEFAULT_STORE_TIMEZONE

                elif store_timezone['ResponseCode'] == 2001:
                    # ====================================================================
                    # Record found in StoreTimezone table
                    # ====================================================================
                    if 'Row' in store_timezone:
                        row = store_timezone['Row']
                        if 'ST_Timezone' in row:
                            store_timezone = row['ST_Timezone']
                else:
                    # ====================================================================
                    # Rows not found in StoreTimezone table, consider default timezone
                    # ====================================================================
                    store_timezone = config.DEFAULT_STORE_TIMEZONE

        return store_timezone

    except Exception:
        raise

    finally:
        del store_timezone


def read_store_status_wrapper(store_id: str) -> list:
    try:
        store_status_rows = []

        # ====================================================================
        # Retrieve all the rows from StoreStatus table for store_id
        # ====================================================================
        store_status = read_store_status(store_id, order_by=config.ORDER_FOR_READING_STORE_STATUS)

        if 'HttpResponseCode' in store_status and store_status['HttpResponseCode'] == 200:
            if 'ResponseCode' in store_status:
                response_code = store_status['ResponseCode']
                if response_code == 3003 or response_code == 2001:
                    store_status_rows = store_status['Rows']

        return store_status_rows

    except Exception:
        raise

    finally:
        del store_status


def read_store_details_wrapper(store_id) -> list:
    try:
        store_details_rows = []

        # ====================================================================
        # Retrieve all the rows from StoreDetails table for store_id
        # ====================================================================
        store_details = read_store_details(store_id, order_by=config.ORDER_FOR_READING_STORE_DETAILS)

        if 'HttpResponseCode' in store_details and store_details['HttpResponseCode'] == 200:
            if 'ResponseCode' in store_details:
                response_code = store_details['ResponseCode']
                if response_code == 3003 or response_code == 2001:
                    store_details_rows = store_details['Rows']

        return store_details_rows

    except Exception:
        raise


def calculate_uptime_last_hour_in_minutes(input_df: pandas.DataFrame):
    try:
        return float(input_df.tail(1)['Uptime_Last_Hour_In_Seconds'].iloc[0]) / 60

    except Exception:
        raise


def calculate_uptime_last_day_in_hours(input_df: pandas.DataFrame):
    try:
        return float(input_df.tail(1)['Uptime_In_Seconds'].iloc[0]) / 3600

    except Exception:
        raise


def calculate_uptime_last_week_in_hours(input_df: pandas.DataFrame):
    try:
        # ====================================================================
        # Get the date from the last row
        # ====================================================================
        current_date = input_df['Date'].iloc[-1]

        # ====================================================================
        # Calculate the date 7 days ago from the current date
        # ====================================================================
        one_week_ago = current_date - timedelta(days=7)

        # ====================================================================
        # Select rows with dates within the last 7 days
        # ====================================================================
        recent_rows = input_df[input_df['Date'] >= one_week_ago]

        # ====================================================================
        # Calculate the sum of Uptime_In_Seconds and convert to hours
        # ====================================================================
        total_uptime_seconds = recent_rows['Uptime_In_Seconds'].sum()
        return float(total_uptime_seconds) / 3600

    except Exception:
        raise


def calculate_downtime_last_hour_in_minutes(input_df: pandas.DataFrame):
    try:
        return float(input_df.tail(1)['Downtime_Last_Hour_In_Seconds'].iloc[0]) / 60

    except Exception:
        raise


def calculate_downtime_last_day_in_hours(input_df: pandas.DataFrame):
    try:
        return float(input_df.tail(1)['Downtime_In_Seconds'].iloc[0]) / 3600

    except Exception:
        raise


def calculate_downtime_last_week_in_hours(input_df: pandas.DataFrame):
    try:
        # ====================================================================
        # Get the date from the last row
        # ====================================================================
        current_date = input_df['Date'].iloc[-1]

        # ====================================================================
        # Calculate the date 7 days ago from the current date
        # ====================================================================
        one_week_ago = current_date - timedelta(days=7)

        # ====================================================================
        # Select rows with dates within the last 7 days
        # ====================================================================
        recent_rows = input_df[input_df['Date'] >= one_week_ago]

        # ====================================================================
        # Calculate the sum of Downtime_In_Seconds and convert to hours
        # ====================================================================
        total_downtime_seconds = recent_rows['Downtime_In_Seconds'].sum()
        return float(total_downtime_seconds) / 3600

    except Exception:
        raise


def read_csv_file(file_path):
    try:
        data = []
        with open(file_path, 'r', newline='') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                data.append(row)
        return data

    except Exception:
        raise
