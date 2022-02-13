"""
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
"""
# %%
import pickle
import os
import pandas as pd
import numpy as np
import pathlib
import sys
from scipy.interpolate import interp1d
import src.preprocess as preprocess

# %%


class Bag_result:
    def __init__(self, bagdata: preprocess.Bag_data, nameoption="") -> None:

        self.bagdata = bagdata
        self.nameoption = nameoption
        self.make_dir_Bag_result()

        self.make_dir_data()
        self.make_dir_plot()
        self.datadict = import_bagdata_as_dict(bagdata)
        self.interpolatefunct_dict = interpolation_datadict(self.datadict)
        self.plotdata_df = make_datadf(self.datadict)
        self.save_processdata()

    def __repr__(self) -> str:
        tem_str = self.bagdata.__repr__()
        rep = str("Bag_result(" + str(self.timeoption) + ") of ") + tem_str
        return rep

    def make_dir_Bag_result(self):
        _analysis_result = os.path.join(
            self.bagdata.destination_folder, "Bag_result" + self.nameoption
        )
        file = pathlib.Path(_analysis_result)
        if file.exists() == False:
            os.mkdir(_analysis_result)
        else:
            print(
                f"The file {_analysis_result} already existedalready exists,\
                  please change name option variable."
            )
            sys.exit()
        self.analysis_results = _analysis_result

    def make_dir_data(self):
        _dir_data = os.path.join(self.analysis_results, "data")
        file = pathlib.Path(_dir_data)
        if file.exists() == False:
            os.mkdir(_dir_data)
        self.data_dir = _dir_data

    def make_dir_plot(self):
        _dir_plot = os.path.join(self.analysis_results, "plots")
        file = pathlib.Path(_dir_plot)
        if file.exists() == False:
            os.mkdir(_dir_plot)
        self.plot_dir = _dir_plot

    def make_plot_data(self):
        return make_datadf(self.datadict)

    def save(self):
        save_bagresult(self)

    def save_processdata(self):
        save_data_in_bagresult(self.datadict, self, "rawdatadict")
        save_data_in_bagresult(self.interpolatefunct_dict, self, "inter_func_dict")
        save_data_in_bagresult(self.plotdata_df, self, "plotdata")


# import bagdata in bag result as dict
def import_bagdata_as_dict(bagdata: preprocess.Bag_data, time_option=1) -> dict:
    """
    load all csv files in target folder and make a dictionary,
    whose values are the csv files and correspond keys
    are transformed in s or min or h (our setting is h (3600))
    ----------
    bagdata: mk.Bagdata
    time_option: int
        1 for s,60 for min, 3600 for h
    Returns
    -------
    dict
        keys: time and values: csv files
    """

    def get_key_csv(x):
        return os.path.splitext(os.path.basename(x))[0]

    def get_value_csv(x):
        return pd.read_csv(x)

    for roots, dirs, files in os.walk(bagdata.target_folder):
        keys_dict_csv = list(map(get_key_csv, files))
        list_roots = [os.path.join(roots, file) for file in files]
        values_dict_csv = list(map(get_value_csv, list_roots))
    keys_dict_csv = [np.round(float(key) / time_option, 8) for key in keys_dict_csv]
    csv_dict = dict(sorted(dict(zip(keys_dict_csv, values_dict_csv)).items()))
    return csv_dict


# save data type in bag result


def save_data_in_bagresult(data, bagresult: Bag_result, nameoption=str):
    if isinstance(data, dict):
        dict_path = os.path.join(bagresult.data_dir, nameoption + ".npy")
        np.save(dict_path, data)
        # print(f"save {nameoption +'.npy'} in {dict_path}")
        # setattr(bagresult, nameoption, dict_path)
        return dict_path
    if isinstance(data, pd.DataFrame):
        df_path = os.path.join(bagresult.data_dir, nameoption + ".csv")
        data.to_csv(df_path, index=False)
        # print(f"save {nameoption +'.csv'} in {df_path}")
        # setattr(bagresult, nameoption, df_path)
        return df_path


# make a interpolation dict from datadict


def interpolation_datadict(datadict: dict) -> dict:
    f_dict = {}
    for time, df in datadict.items():
        tem_x = np.array([df["Frequency(ppm)"]]).flatten()
        tem_y = np.array([df["Intensity"]]).flatten()
        tem_f = interp1d(tem_x, tem_y, kind="cubic")
        f_dict.update({time: tem_f})
    return f_dict


def make_datadf(datadict: dict) -> pd.DataFrame:
    f_dict = interpolation_datadict(datadict)
    time_col_index = list(f_dict.keys())
    ppm_col = list(np.linspace(-26.3, 35.82, 65536))  # make it as parameters
    cols_name = ["Frequency"] + time_col_index
    data_df = pd.DataFrame(columns=cols_name)
    data_df["Frequency"] = ppm_col
    for t in time_col_index:
        data_df[t] = f_dict[t](data_df["Frequency"].values)
    return data_df


def filter_datadf(
    df, timestr: float, timeend: float, ppmstr: float, ppmend: float
) -> pd.DataFrame:
    """
    function to filter the data df with desired ppm and time
    """

    tem_df = df.loc[(df["Frequency"] >= ppmstr) & (df["Frequency"] <= ppmend)]
    time_col_index = [col for col in list(tem_df.columns) if col != "Frequency"]
    select_time_col = [
        col for col in time_col_index if (col >= timestr) and (col <= timeend)
    ]
    tem_col = ["Frequency"] + select_time_col
    return tem_df[tem_col]


# save and load bag_result


def save_bagresult(bagresult: Bag_result):
    bagresult_path = os.path.join(bagresult.analysis_results, "bagresult.pkl")
    pickle.dump(bagresult, open(bagresult_path, "wb"))
    print(f"save {type(bagresult)} in {bagresult_path}")
    return bagresult_path


def load_bagresult(bagresult_path):
    file = pathlib.Path(bagresult_path)
    if file.exists() == False:
        print(f"there is no bagresult object")
    else:
        return pickle.load(open(bagresult_path, "rb"))
