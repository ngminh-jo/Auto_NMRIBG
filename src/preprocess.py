"""
This preprocess.py is developed for data processing and provides the data for analysis tasks.
- The Bag_data class is responsible for loading and preprocessing the csv files, the NMR exports, each time. 
- Create a new Bag_data object in destination_folder from the NMR source_folder and start_date_time.
- All csv files created after the start date in the source folder will be stored in the destination folder and renamed to Time_Gap.
- The information of all csv files will be saved as information.csv in the destination folder.
- destination_folder: where you want to save the data of the current experiment.
- source_folder: where the NMR device exports the data to.
- start_date_time: the desired start time for importing the files from source_folder.
- target_folder: where all imported csv files are located.
- information: The information of all imported csv files.
- Each bag_data instance can be store and load with the save_bagdata and load_bagdata functions. 
- save_bagdata(bagdata: Bag_data) takes a bag_data instance as input and store this bag_data in the destination_folder.
- load_bagdata(destination_folder: os.path) takes destination_folder path as input. In each destination_folder, there is only one bag_data.pkl instance.
For example:
source_1 = r'/Users/nguyenminhhieu/Documents/Job/HIWI_JOB/source_live_data'
destination_1 = r'/Users/nguyenminhhieu/Documents/Job/HIWI_JOB/live_data'
start_date_time_1 = datetime(2021, 6, 15, 0, 0, 0, 0)
bagdata_1 = Bag_data(source_1, destination_1, start_date_time_1)
bagdata_1.__repr__
Bag_data(2021-06-15 00:00:00) 
process all csv files created in source_folder after start_date_time:2021-06-15 00:00:00
# saving and loading bag_data instance.
save(bagdata_1)
bagdata_1 = load(destination_1)
"""

import pickle
import os
import shutil
from dateutil import parser
from datetime import datetime
import pandas as pd
import numpy as np
import pathlib
import sys


class Bag_data:
    """
    Create a new data_batch object in destination_folder from the given source_folder and start_date_time.
    All the csv files in which are created after start_date_time in source_folder to target_folder and rename it as Time_Gap.
    The information of all the csv files will be saved as information.csv  in destination_folder.
        destination_folder: where you want to store the data of the current experiment.
        source_folder: where the NMR machine exports the data.
        start_date_time: the desired start time for input the files from source_folder.
        target_folder: where all the csv files are.
        information: The information of all the csv files.
    """

    def __init__(
        self, source_folder: str, destination_folder: str, start_date_time: datetime
    ) -> None:
        """
        destination_folder: where you want to store the data of the current experiment.
        source_folder: where the NMR machine exports the data.
        start_date_time: the desired start time for input the files from source_folder.
        target_folder: where all the csv files are.
        information: The information of all the csv files.
        """

        self.source_folder = source_folder
        self.destination_folder = destination_folder
        self.start_date_time = start_date_time
        self.target_folder = self.make_dir_NMR_Data()
        self.load_csvfiles()

    def __repr__(self) -> str:
        rep = "Bag_data(" + str(self.start_date_time) + ")"
        return rep

    def make_dir_NMR_Data(self) -> str:
        """
        The make_dir_NMR_Data create the NMR_Data directory in the destination_folder,
        all the copied CSVs will be saved here.
        """
        _target_folder = os.path.join(self.destination_folder, "Bag_data")
        file = pathlib.Path(_target_folder)
        if file.exists() == False:
            os.mkdir(_target_folder)
        else:
            print(
                f"The file { _target_folder} already existed,please change the destination folder."
            )
            sys.exit()
        return _target_folder

    def load_csvfiles(self):
        self.information = makefile_with_time(
            self.source_folder, self.target_folder, self.start_date_time
        )

    def save(self):
        save_bagdata(self)


def makefile_with_time(
    source_folder: str, target_folder: str, start_date_time: datetime
):
    """
    The  makefile_with_time(source_folder,target_folder, start_date_time) will
    copy all the csv files which are created after start_date_time in source_folder
    to target_folder and rename it as Time_Gap. The information of all the csv
    files will be saved as information.csv in parent_dir of target_foler.
    ----------
    source_folder: str
        where the NMR device exports the data to.
    target_folder: str
        where all imported csv files are located.
    start_date_time: datetime
        the desired start time for importing the files from source_folder.
    Returns
    -------
    infor_path: str
        The information of all imported csv files.
    """
    df = get_csv_file_with_time(source_folder, start_date_time)
    if len(df) > 0:
        for i in range(len(df)):
            shutil.copy(
                df["Source_Path"][i],
                os.path.join(target_folder, str(df["TimeGap"][i]) + ".csv"),
            )
        os.chdir(target_folder)

    infor_path = os.path.join(os.path.join(target_folder, ".."), "information.csv")
    df.to_csv(infor_path, index=False)
    return infor_path


def get_csv_file_with_time(source_folder: str, start_date_time: datetime):
    """The get_csv_file_with_time get the information of all the csv files,
    which are created after start_date_time in source folder.
    This returns a padas dataframe with column 'start_time', 'path', 'time_gap'.
    """
    li_file_path = []
    li_file_name = []
    for root, dirs, files in os.walk(source_folder):
        for tem_file in files:
            file = str(tem_file)
            if file.endswith("processed.csv"):
                tem_name = get_name_start_time(root)
                if tem_name > start_date_time:
                    li_file_path.append(os.path.join(root, file))
                    li_file_name.append(tem_name)
    if len(li_file_name) > 0:
        df = pd.DataFrame(
            list(zip(li_file_name, li_file_path)), columns=["DateTime", "Source_Path"]
        )
        tem_df = df.sort_values(by="DateTime", ascending=True).reset_index(drop=True)
        tem_time_gap = tem_df["DateTime"][:] - tem_df["DateTime"][0]
        Time_Gap = []
        for i in range(len(tem_time_gap)):
            Time_Gap.append(int(np.floor(tem_time_gap[i].total_seconds())))
        tem_df["TimeGap"] = Time_Gap
        return tem_df
    else:
        print(
            f"there is no csv file in {source_folder},created after {start_date_time}"
        )
        df = pd.DataFrame(columns=["DateTime", "Source_Path", "TimeGap"])
        return df


def get_name_start_time(csv_path: str):
    """The get_name_start_time will go to the path,
    where the exported csv is and read the acqu.par as text files.
    The value of start_time will be taken as output.
    """
    os.chdir(csv_path)
    df = pd.read_csv("acqu.par", delimiter="=")
    name = df[df.columns[1]][2]
    return parser.parse(name.replace(" ", "")[1:-1])


def list_all_folder(folder: str):
    tem_ls_dir = list(os.listdir(folder))
    print(tem_ls_dir)
    return tem_ls_dir


# save and load bagdata


def save_bagdata(bagdata: Bag_data):
    bagdata_path = os.path.join(bagdata.destination_folder, "bagdata.pkl")
    pickle.dump(bagdata, open(bagdata_path, "wb"))
    print(f"save {type(bagdata)} in {bagdata_path}")
    return bagdata_path


def load_bagdata(bagdata_path: os.path):
    file = pathlib.Path(bagdata_path)
    if file.exists() == False:
        print(f"there is no bagdata object")
    else:
        return pickle.load(open(bagdata_path, "rb"))
