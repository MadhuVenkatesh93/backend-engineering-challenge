# Moving average cli tool

## Requirements

For a collection of event objects, each with the following structure:
```json
{
	"timestamp": "2018-12-26 18:12:19.903159",
	"translation_id": "5aa5b2f39f7254a75aa4",
	"source_language": "en",
	"target_language": "fr",
	"client_name": "easyjet",
	"event_name": "translation_delivered",
	"duration": 20,
	"nr_words": 100
}
```
>we want to count, for each minute, the moving average delivery time of all translations for the past 10 minutes

Notes:
* "for each minute" pertains to each minute within the range of the earliest and latest translation event
* delivery time is the `duration` key in the translation event object above
* the time window in minutes should be a variable set on execution
* "the past X (e.g. 10) minutes" pertains to the preceeding X minutes of events for each minute within the range of the entire input collection
* Can we assume that the input collection is always sorted chronologically?

The output should have the following structure for each minute in the specified window:

```json
{ "date": "2018-12-26 18:11:00", "average_delivery_time": 0 }
```

## Approach and Solution

* Since it's not a standard JSON file, read the file line by line and save it in the DataFrame to ease the process.
* we can have multiple number of transactions for every minute. to generalise, groupby minute to get the avegare. 
* moving avaerage = sum of last x minutes trasactional time / number of non zero duration in last X minutes 
* Simple plot to visualise the moving average


![Screenshot](/moving_avg.png?raw=true "Moving Average")

## Requirements to execute the code
* Python==3.5.2
* matplotlib==2.0.2
