from datetime import datetime

import pandas

from store_monitoring.Helper import calculate_time_difference, calculate_uptime_last_hour_in_minutes, \
    calculate_uptime_last_day_in_hours, calculate_uptime_last_week_in_hours, calculate_downtime_last_hour_in_minutes, \
    calculate_downtime_last_day_in_hours, calculate_downtime_last_week_in_hours


def process_store_with_specified_time(store_details: list,
                                      store_status_df: pandas.DataFrame,
                                      store_id: str) -> dict:
    try:
        store_details_df = pandas.DataFrame(store_details)

        # ====================================================================
        # Group by on the basis of same date
        # ====================================================================
        grouped_on_date = store_status_df.groupby(store_status_df['SS_LocalTimestamp'].dt.date)
        uptime_and_downtime = grouped_on_date.apply(calculate_final_uptime_and_downtime_for_time_specified,
                                                    store_details_df=store_details_df,
                                                    store_id=store_id)

        if len(uptime_and_downtime) > 0:
            uptime_and_downtime_list = uptime_and_downtime.tolist()
            filtered_uptime_and_downtime_list = [item for item in uptime_and_downtime_list if item is not None]
            output_df = pandas.DataFrame(filtered_uptime_and_downtime_list)

            # ====================================================================
            # Calculate final output
            # ====================================================================
            final_output = dict()
            final_output['store_id'] = store_id
            final_output['uptime_last_hour(in minutes)'] = calculate_uptime_last_hour_in_minutes(output_df)
            final_output['uptime_last_day(in hours)'] = calculate_uptime_last_day_in_hours(output_df)
            final_output['uptime_last_week(in hours)'] = calculate_uptime_last_week_in_hours(output_df)
            final_output['downtime_last_hour(in minutes)'] = calculate_downtime_last_hour_in_minutes(output_df)
            final_output['downtime_last_day(in hours)'] = calculate_downtime_last_day_in_hours(output_df)
            final_output['downtime_last_week(in hours)'] = calculate_downtime_last_week_in_hours(output_df)
            return final_output

    except Exception:
        raise


def calculate_final_uptime_and_downtime_for_time_specified(current_group: pandas.DataFrame,
                                                           store_details_df: pandas.DataFrame,
                                                           store_id: str) -> dict:
    try:
        # ====================================================================
        # Get the row from store_details_df['SD_Day'] SD_Day = group['SS_Day']
        # This will help us understand the StartTime and EndTime of the store on the given Day
        # ====================================================================
        store_day_details = store_details_df[store_details_df['SD_Day'] == int(current_group['SS_Day'].iloc[0])]

        if len(store_day_details) > 0:
            current_day = int(store_day_details['SD_Day'].iloc[0])
            store_start_time = datetime.strptime(store_day_details['SD_StartTimeLocal'].iloc[0],
                                                 '%H:%M:%S').time()
            store_end_time = datetime.strptime(store_day_details['SD_EndTimeLocal'].iloc[0],
                                               '%H:%M:%S').time()

            # ====================================================================
            # Extract time from the Timestamp from group
            # ====================================================================
            current_group['Time'] = current_group['SS_LocalTimestamp'].dt.time
            current_date = current_group['SS_LocalTimestamp'].dt.date.iloc[0]

            # ====================================================================
            # Filter the rows that fall within the StartTime and EndTime of the store
            # ====================================================================
            filtered_df = current_group[(current_group['Time'] >= store_start_time) &
                                        (current_group['Time'] <= store_end_time)]

            if len(filtered_df) > 0:
                # ====================================================================
                # Add a new column 'Previous_Time' with the time of the previous row
                # ====================================================================
                filtered_df['Previous_Time'] = filtered_df['Time'].shift(1)

                # ====================================================================
                # Calculate the uptime and downtime for the store
                # ====================================================================
                result_df = filtered_df.apply(calculate_uptime_and_down_for_time_specified,
                                              store_start_time=store_start_time,
                                              axis=1,
                                              result_type='expand')

                # ====================================================================
                # Rename the columns of the result DataFrame
                # ====================================================================
                result_df.columns = ['Uptime_In_Seconds', 'Downtime_In_Seconds',
                                     'Uptime_Last_Hour_In_Seconds', 'Downtime_Last_Hour_In_Seconds']

                # ====================================================================
                # Combine the original DataFrame and the result DataFrame
                # ====================================================================
                final_df = pandas.concat([filtered_df, result_df], axis=1)

                output_dict = dict()
                output_dict['Store_Id'] = store_id
                output_dict['Day'] = current_day
                output_dict['Date'] = current_date
                output_dict['Uptime_In_Seconds'] = int(final_df['Uptime_In_Seconds'].sum())
                output_dict['Downtime_In_Seconds'] = int(final_df['Downtime_In_Seconds'].sum())
                output_dict['Uptime_Last_Hour_In_Seconds'] = int(final_df['Uptime_Last_Hour_In_Seconds'].iloc[-1])
                output_dict['Downtime_Last_Hour_In_Seconds'] = int(final_df['Downtime_Last_Hour_In_Seconds'].iloc[-1])
                return output_dict

    except Exception:
        raise


def calculate_uptime_and_down_for_time_specified(current_row: pandas.Series,
                                                 store_start_time: str):
    try:
        uptime_in_seconds = 0
        downtime_in_seconds = 0
        uptime_last_hour_in_seconds = 0
        downtime_last_hour_in_seconds = 0

        current_time = current_row['Time']
        previous_time = current_row['Previous_Time']
        if previous_time is None:
            # ====================================================================
            # Calculate the difference
            # ====================================================================
            difference_in_time = calculate_time_difference(store_start_time, current_time)

        else:
            difference_in_time = calculate_time_difference(previous_time, current_time)

        if current_row['SS_StoreStatus'] == 'active':
            # ====================================================================
            # The store has been active for the difference_in_time
            # ====================================================================
            uptime_in_seconds += difference_in_time
            uptime_last_hour_in_seconds = difference_in_time

        else:
            # ====================================================================
            # The store has been inactive for the difference_in_time
            # ====================================================================
            downtime_in_seconds += difference_in_time
            downtime_last_hour_in_seconds = difference_in_time

        return uptime_in_seconds, downtime_in_seconds, uptime_last_hour_in_seconds, downtime_last_hour_in_seconds

    except Exception:
        raise
