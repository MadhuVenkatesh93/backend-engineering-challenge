import pandas as pd
import argparse 
import os
import sys
import json 
from datetime import tzinfo, timedelta, datetime
import matplotlib.pyplot as plt
from matplotlib import dates
from matplotlib.dates import date2num


def read_and_validate_args():	

	parser = argparse.ArgumentParser(description='To computes moving average.!')
	parser.add_argument('--input_file', help = 'Input file name.!')
	parser.add_argument('--window_size', type=int, default = 1, help = 'Window size. default is 1.!')
	args = parser.parse_args()


	# check for input file
	if args.input_file is None:
	    print('Enter a valid input file name!')
	    sys.exit(1)

	# check for valid input file
	if not os.path.isfile(args.input_file):
	    print('Invalid input file!')
	    sys.exit(1)

	# validate window size
	if args.window_size <= 0:
	    print('Invalid window size!')
	    sys.exit(1)

	return args
 

	
def read_input_file():
 
	# Since it is not a standart .json file, read the file line by line.
	# for our conviniance, return the data in a DataFrame
	with open(args.input_file, 'r') as f:
		data = [json.loads(line) for line in f]

	data = pd.DataFrame(data)

	return data


def calculate_moving_avg(data,args):

	# helper function 
	def running_mean(l, N):
	    sum = 0

	    # window sinze can not be greater than mac length of time series
	    N = min(N, len(l) )

	    result = list( 0 for x in l)
	    valid_n = list( 1 for x in l)

	    # devide the sum by number of non zero durations in last X minute transactions
	    for i in range( 0, len(l)):
	    	count = 0
	    	for j in range(max(0, i-N+1), i+1):
	    		if l[j] > 0:
	    			count += 1
	    	if count > 0:
	    		valid_n[i] = count
	 
	 	# calculate moving averae for first N events
	    for i in range( 0, N ):
	    	sum = sum + l[i]
	    	result[i] = sum / valid_n[i]

	    # calculate moving average for remaining events 
	    for i in range( N, len(l) ):
	    	sum = sum - l[i-N] + l[i]
	    	result[i] = sum / valid_n[i]

	    return result



	# Objective: we're instered in calculating, for every minute, a moving average of the translation delivery time for the last X minutes.
	# Scenario 1: If there exists only one transactional record for every minute, calcu moving average for last X translations ( X minutes )
	# Scenario 2: If there exists more than one one translations per minute, we need to consider all translations for last X minutes. 
	# To generalise the scenario, we can groupby by time ( every monute) and have aggregated average for each timestamp ( for esch minute) 



	# ignore the second and milisecond data
	data['timestamp'] = data['timestamp'].apply(lambda x: x[:16]) 
	data['timestamp'] = pd.to_datetime(data['timestamp'], format='%Y-%m-%d %H:%M')

	# note down start and end time 
	start_time = min(data['timestamp'])# - timedelta(minutes = 1) 
	end_time = max(data['timestamp']) + timedelta(minutes = 1)  

	# move the timestamp to next minute
	data['timestamp'] = data['timestamp'] + timedelta(minutes = 1) 


	# we might not have translations for every minute. but we do need moving average for every minute. So create a DataFrame with timeseries data 
	# from start time to end time. Then merge with original data to. This will yield the data what we need. 
	date_range = pd.date_range(start = start_time, end=end_time, freq='min')
	output = pd.DataFrame(date_range, columns={'timestamp'})
	output = pd.merge(output, 	data[['timestamp','duration']], how='left', left_on= 'timestamp', right_on= 'timestamp').fillna(0) 
	output = output.groupby(by=['timestamp'])['duration'].mean().reset_index()	


	# using helper funtion running_mean(), calculate the moving average
	output['moving_avg'] = running_mean(output['duration'], args.window_size)

	# drop the unwanted columns
	output.drop(['duration'], axis = 1, inplace = True)
	 

	return output 

def visualise(data):
	 
	# plot moving avg vs time
    datemin = min(data['timestamp']) -timedelta(minutes = 1) 

    datemax = max(data['timestamp'])

    strtime = [datetime.strptime(str(i),'%Y-%m-%d %H:%M:%S') for i in data['timestamp'].tolist()]
    dates_list = date2num(strtime) 

    fig = plt.figure(figsize=(20, 10))
    temp = fig.add_subplot(111) 
    temp.set_xlim(datemin, datemax) 
    temp.set_ylabel('Moving Average for window size size {}'.format(args.window_size) )
    temp.set_xlabel('Date' )

    temp.plot_date(dates_list, data['moving_avg'], xdate = True, ls = '-')
    plt.gcf().autofmt_xdate()
    plt.savefig('{}/moving_avg.png'.format(os.getcwd()), dpi=300, type='png')


def save_data(data):
	# helper function to format the output string
	def dict_to_str(line):
		out = '{{"date" {}, "average_delivery_time": {}}}'.format(line['timestamp'].strftime("%Y-%m-%d %H:%M:%S"), str(int(line['moving_avg']))\
		if  line['moving_avg'].is_integer() else str(round(line['moving_avg'],2)))
		return out



	# save the dave as required
	data = data.to_dict('records')

	with open('output.json', 'w') as f:
		for line in data[:-1]:
			f.write(dict_to_str(line) + '\n')

		f.write(dict_to_str(data[-1]))


def main():
	global args

	# read and validate all argumets 
	args = read_and_validate_args()

	# read the input file if it exists 
	input_data = read_input_file()

	# calculate the moving average
	output_data = calculate_moving_avg(input_data,args)

	# save the data in output log
	save_data(output_data)

	# visualise the data in a plot
	# uncomment this funtion to save the graph
	visualise(output_data)

if __name__ == '__main__':
	main()