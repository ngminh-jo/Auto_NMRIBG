# project Benchtop NMR

Goal: automated and autonomous Benchtop NMR control for a microfluidic bioreactor.

## Table of Contents
  1. [preprocess.py](#preprocess.py)
  2. [storeresults.py](#storeresults.py)
  3. [peak_area.py](#peak_area.py)
  4. [plot.py](#plot.py)
  5. [analysis.py](#analysis.py)
  6. [live_dev.py](#live_dev.py)

## preprocess.py
This preprocess.py is developed for data processing and provides the data for analysis tasks.

- The Bag_data class is responsible for loading and preprocessing the csv files, the NMR exports, each time. 
- Create a new Bag_data object in destination_folder from the NMR source_folder and start_date_time.
- All csv files created after the start date in the source folder will be stored in the destination folder and renamed to Time_Gap.
- The information of all csv files will be saved as information.csv in the destination folder.
- destination_folder: where you want to save the data of the current experiment.
- source_folder: where the NMR device exports the data to.
- start_date_time: the desired start time for importing the files from source_folder.
- target_folder: where all imported csv files are located.
- information_df: The information of all imported csv files.
For example:
```python
source_1 = r'/Users/nguyenminhhieu/Documents/Job/HIWI_JOB/source_live_data'
destination_1 = r'/Users/nguyenminhhieu/Documents/Job/HIWI_JOB/live_data'
start_date_time_1 = datetime(2021, 6, 15, 0, 0, 0, 0)
data = Bag_data(source_1, destination_1, start_date_time_1)
data.__repr__
```
Bag_data(2021-06-15 00:00:00) 

is processed all the csv files, which are created after start_date_time:2021-06-15 00:00:00 in source_folder

## storeresults.py
This store_results.py is developed for storing results for later analysis.
- The Bag_result class is responsible for storing results (data, plots) which are from Bad_data class . 
- Create a new Bag_result object from a existed bag_data instance.
- New folder Bag_result_nameoption is created, the nameoption can be change as desired. 
- In the Bag_result_nameoption folder, there are datasets folder and docs folder. All later analysis should be store in here.
- save_bagresult(bagresult: Bag_result) takes a bag_result instance as input and store this bag_data in the Bag_result_nameoption folder.
- load_bagresult(destination_folder: os.path, bagresult_name: str) takes destination_folder path and bagresult_name  as input.
 In each destination_folder, it is possible to have more than one Bag_result_nameoption instance,
  but in each Bag_result_nameoption there is only one bagresult.pkl  
For example:
# create a bagdata instance
```python
source_1 = r'/Users/nguyenminhhieu/Documents/Job/HIWI_JOB/source_live_data'
destination_1 = r'/Users/nguyenminhhieu/Documents/Job/HIWI_JOB/live_data'
start_date_time_1 = datetime(2021, 6, 15, 0, 0, 0, 0)
bagdata_1 = preprocess.Bag_data(source_1, destination_1, start_date_time_1)
bagdata_1.__repr__
#Bag_data(2021-06-15 00:00:00) 
# We create a bag_result instance from this bag_data
bagresult_1 = Bag_result(bagdata=bagdata_1, nameoption='_1')
# saving and loading bag_result instance
save_bagresult(bagresult= bag_result_1)
load_bagresult(destination_folder= destination_1, bagresult_name='bagresult_1')
```
