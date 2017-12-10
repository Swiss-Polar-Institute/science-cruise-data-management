import pandas

def calculate_gaps(data):
    "Calculate gaps in pandas dataframe data, where data is in a dictionary with the keys: filename, start date and end date of file."

    # Create the dataframe from a dictionary of the data.
    df = pandas.DataFrame(data)

    # Sort the rows in order of the file start date.
    df.sort_values('start_date', inplace=True)

    # Ensure the file start and end dates are in datetime format.
    df['start_date'] = pandas.to_datetime(df['start_date'], format='%Y-%m-%d %H:%M:%S')
    df['end_date'] = pandas.to_datetime(df['end_date'], format='%Y-%m-%d %H:%M:%S')

    # Create a copy of the dataframe with a new index, which is integers, incrementing from 0 to the number of rows - 1 in the dataframe.
    ordered_df = df.copy()
    ordered_df.index = range(len(df))

    # In order to find the gaps in between data collection we will use the difference between the start time of a file and the end time of the previous file. The difference must be greater than 5 minutes for it to be considered a new set of data collection and therefore a new event.

    # The period is a dictionary of the time the data are being recorded (i.e. there are files). It is a dictionary and will have keys "starts" and "stops" which are the start and end times of the data collection, considering the 5 minute gaps.
    period = {}

    # If we consider the first file, this must be the start of the first event, so this is a special case. Therefore we assign the start time of this file to be the start time of the first period.
    period['starts'] = convert_to_string(ordered_df['start_date'][0])

    i = 1

    # Each of the periods (start and end times of data recording) will be stored in a list called file periods.
    file_periods = []

    # Run through each row of the ordered data frame and when reaching a gap of more than 5 minutes (or 300 seconds), create the end of the last period and the beginning of the new period.
    while i < len(ordered_df):
        if (ordered_df['start_date'][i] - ordered_df['end_date'][i - 1]).seconds > 59:
            period['stops'] = convert_to_string(ordered_df['end_date'][i - 1])
            file_periods.append(period)

            period = {}
            period['starts'] = convert_to_string(ordered_df['start_date'][i])
            # print("Processing ", new_df['filename'][i], "Found gap, start:", new_df['filename'][i], "end: ", new_df['filename'][i-1])

        i = i + 1

    # The last file in the dataframe is also a special case. The end of this file will always be the end of the event.
    period['stops'] = convert_to_string(ordered_df['end_date'][i - 1])

    #print(period)
    return file_periods


def save_gaps():
    #TODO
    pass

def convert_to_string(timedelta):
    return timedelta.strftime("%Y-%m-%d %H:%M:%S")

