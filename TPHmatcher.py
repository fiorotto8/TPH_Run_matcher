import numpy as np
import pandas as pd
import csv
from datetime import datetime, timedelta
import argparse

def find_nearest_dates(list1, list2):
    """
    For each datetime in list1, find the nearest datetime in list2.

    :param list1: List of datetime objects to find nearest dates for.
    :param list2: List of datetime objects to search within.
    :return: List of datetime objects from list2 nearest to each datetime in list1.
    """
    nearest_dates = []
    for dt1 in list1:
        # Find the nearest datetime in list2 by minimizing the absolute difference
        nearest_date = min(list2, key=lambda dt2: abs(dt2 - dt1))
        nearest_dates.append(nearest_date)
    return nearest_dates

parser = argparse.ArgumentParser(prog='TPHmatcher.py',description='Matches the date from Runlog with the TPH from Arduino',epilog='Text at the bottom of help')
parser.add_argument('-r','--runlog',help='Path of the Runlog file', action='store', type=str,default='./Runlog_Feb2024.csv')
parser.add_argument('-a','--arduino',help='Path of the arduino file', action='store', type=str,default="./TPH_log_Feb2024.csv")
parser.add_argument('-o','--output',help='Path of the output file', action='store', type=str,default="../Feb24Out.csv")
args = parser.parse_args()

# Update file path to the newly uploaded file
file_path = args.runlog

# Reset lists to store the extracted data
runs = []
timestamps_runlog = []

# Open and read the uploaded CSV file
with open(file_path, 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        # Extract the first column (ID) and the third column (timestamp)
        runs.append(row[0])
        row_dt = datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S')
        timestamps_runlog.append((row_dt))

#print(timestamps_runlog)

cols=["Time","Temperature","Pressure","Humidity","VOC"]
df_tph=pd.read_csv(args.arduino, header=None, names=cols,sep=";")

# Convert the 'Time' column to datetime objects for comparison
df_tph['Time'] = pd.to_datetime(df_tph['Time'], format='%Y-%m-%d_%H:%M:%S.%f')

# Function to find the nearest time in df_tph for each timestamp in timestamps_runlog
def find_nearest(row, df):
    # Calculate the absolute difference between the target time and all times in the df
    time_diff = abs(df['Time'] - row)
    # Find the index of the smallest time difference
    min_diff_idx = time_diff.idxmin()
    # Return the row from df that has the smallest difference
    return df.iloc[min_diff_idx]

nearest_rows_list = []  # Use a list to collect the rows

for timestamp in timestamps_runlog:
    nearest_row = find_nearest(timestamp, df_tph)
    nearest_rows_list.append(nearest_row)  # Append the row to the list

# Concatenate all the rows in the list into a new DataFrame
nearest_rows = pd.concat(nearest_rows_list, axis=1).transpose()

# Reset index if desired
nearest_rows.reset_index(drop=True, inplace=True)

# Ensure the length of the 'runs' list matches the number of rows in 'nearest_rows' DataFrame
if len(nearest_rows) == len(runs):
    nearest_rows['Run'] = runs
else:
    print("The lengths do not match. Please check your data.")

# Save the DataFrame to a CSV file
nearest_rows.to_csv(args.output, index=False)
