import pandas

from store_monitoring.Helper import calculate_time_difference, calculate_uptime_last_hour_in_minutes, \
    calculate_uptime_last_day_in_hours, calculate_uptime_last_week_in_hours, calculate_downtime_last_hour_in_minutes, \
    calculate_downtime_last_day_in_hours, calculate_downtime_last_week_in_hours


def process_store_for_24_7(store_status_df: pandas.DataFrame,
                                 store_id: str) -> dict:
    try:
        # ====================================================================
        # Group by on the basis of same date
        # ====================================================================
        grouped_on_date = store_status_df.groupby(store_status_df['SS_LocalTimestamp'].dt.date)
        uptime_and_downtime = grouped_on_date.apply(calculate_final_uptime_and_downtime_for_24_7, store_id=store_id)

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


def calculate_final_uptime_and_downtime_for_24_7(current_group: pandas.DataFrame,
                                                 store_id: str):
    try:
        # ====================================================================
        # Extract time from the Timestamp from group
        # ====================================================================
        current_group['Time'] = current_group['SS_LocalTimestamp'].dt.time
        current_date = current_group['SS_LocalTimestamp'].dt.date.iloc[0]
        current_day = int(current_group['SS_Day'].iloc[0])

        # ====================================================================
        # Add a new column 'Previous_Time' with the time of the previous row
        # ====================================================================
        current_group['Previous_Time'] = current_group['Time'].shift(1)

        result_df = current_group.apply(calculate_uptime_and_downtime_for_24_7,
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
        final_df = pandas.concat([current_group, result_df], axis=1)

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


def calculate_uptime_and_downtime_for_24_7(current_row: pandas.Series):
    try:
        uptime_in_seconds = 0
        downtime_in_seconds = 0
        uptime_last_hour_in_seconds = 0
        downtime_last_hour_in_seconds = 0

        current_time = current_row['Time']
        previous_time = current_row['Previous_Time']

        if previous_time is None:
            current_time_in_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second
            if current_row['SS_StoreStatus'] == 'active':
                # ====================================================================
                # The store has been active
                # ====================================================================
                uptime_in_seconds += current_time_in_seconds
                uptime_last_hour_in_seconds = current_time_in_seconds

            elif current_row['SS_StoreStatus'] == 'inactive':
                # ====================================================================
                # The store has been inactive
                # ====================================================================
                downtime_in_seconds += current_time_in_seconds
                downtime_last_hour_in_seconds = current_time_in_seconds

        else:
            # ====================================================================
            # Calculate the difference
            # ====================================================================
            difference_in_time = calculate_time_difference(previous_time, current_time)

            if current_row['SS_StoreStatus'] == 'active':
                # ====================================================================
                # The store has been active for the difference_in_time
                # ====================================================================
                uptime_in_seconds += difference_in_time
                uptime_last_hour_in_seconds = difference_in_time

            elif current_row['SS_StoreStatus'] == 'inactive':
                # ====================================================================
                # The store has been inactive for the difference_in_time
                # ====================================================================
                downtime_in_seconds += difference_in_time
                downtime_last_hour_in_seconds = difference_in_time

        return uptime_in_seconds, downtime_in_seconds, uptime_last_hour_in_seconds, downtime_last_hour_in_seconds

    except Exception:
        raise
