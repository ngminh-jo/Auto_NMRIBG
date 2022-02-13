import time
import os
import shutil
import pandas as pd
import numpy as np
import os
import shutil
import pandas as pd
import numpy as np
from scipy.integrate import quad
from scipy.interpolate import interp1d
import warnings

warnings.filterwarnings("ignore")
from functools import reduce
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import src.preprocess as preprocess
import src.analysis as analysis


class Live_analysis:
    def __init__(self, baganalysis: analysis.Bag_analysis):
        self.baganalysis = baganalysis
        self.w = Watcher(self.baganalysis)

    def live_update(self):
        self.w.run()


class Watcher:
    warnings.filterwarnings("ignore")

    def __init__(self, baganalysis: analysis.Bag_analysis):
        self.observer = Observer()
        self.baganalysis = baganalysis
        self.DIRECTORY_TO_WATCH = baganalysis.bagresult.bagdata.source_folder

    def run(self):
        event_handler = Handler(self.baganalysis)
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        print("__ Start __")
        try:
            while True:
                time.sleep(1)

        except:
            self.observer.stop()
            print("__Finalupdate__")
            update_baganalysis(self.baganalysis)
            print("__ Finish __")

        self.observer.join()


class Handler(FileSystemEventHandler):
    def __init__(self, baganalysis: analysis.Bag_analysis):
        super().__init__()
        self.baganalysis = baganalysis
        self.csv_dict = {}

    warnings.filterwarnings("ignore")

    def on_created(self, event):
        file = str(event.src_path)
        if file.endswith("processed.csv"):
            warnings.filterwarnings("ignore")

            # print(event.src_path)
            root = os.path.split(event.src_path)[0]
            start_time = preprocess.get_name_start_time(root)
            if start_time in set(self.csv_dict.keys()):
                print("_____" * 10)
                print(f"update {start_time}")
                self.csv_dict[start_time] = event.src_path

            else:
                # load new csv files in targetfolder
                print("_____" * 10)
                if len(self.csv_dict) > 0:
                    # update baganalysis
                    update_baganalysis(self.baganalysis)
                    # update baganalysis.analysis_df

                # update bagdata.information
                update_bagdata(self.baganalysis.bagresult.bagdata, event)
                print(f"new measurement {start_time}")
                self.csv_dict.update({start_time: event.src_path})


def update_newanalysis(f_0, t_0, baganalysis: analysis.Bag_analysis):
    chemicals, sty_const, c0_tmsp, tmsp = (
        baganalysis.chemicals,
        baganalysis.sty_const,
        baganalysis.c0_tmsp,
        baganalysis.tmsp,
    )
    if tmsp not in set(chemicals):
        chemicals.append(tmsp)
    df_list = []
    for chemical_shift in chemicals:
        # print(chemical_shift)
        peak_area_dict = {}
        peak_area = np.abs(quad(f_0, chemical_shift.ppmstr, chemical_shift.ppmend))
        peak_area_dict.update({t_0: peak_area[0] * 10})
        peak_area_df = pd.DataFrame(
            data=list(peak_area_dict.items()), columns=["Time", chemical_shift.name]
        )
        df_list.append(peak_area_df)
    peakarea_df = reduce(lambda df1, df2: pd.merge(df1, df2, on="Time"), df_list)
    analysis_df = peakarea_df
    # signal per proton
    for name in list(analysis_df.columns):
        for chemical in chemicals:
            if name == chemical.name:
                # print(chemical)
                analysis_df[str(name) + "_per_proton"] = (
                    analysis_df[name] / chemical.nr_proton
                )
    # concentration
    for name in list(analysis_df.columns):
        for chemical in chemicals:
            if name == chemical.name and chemical != tmsp:
                analysis_df[str(name) + "_concentration"] = (
                    c0_tmsp
                    * analysis_df[str(name) + "_per_proton"]
                    / analysis_df[str(tmsp.name) + "_per_proton"]
                )
    # STY
    for name in list(analysis_df.columns):
        for chemical in chemicals:
            if name == chemical.name and chemical != tmsp:
                analysis_df[str(name) + "_sty"] = (
                    sty_const * analysis_df[str(name) + "_concentration"]
                )
    return analysis_df


def update_baganalysis(baganalysis: analysis.Bag_analysis):
    old_infor = pd.read_csv(baganalysis.bagresult.bagdata.information)
    print(f'copy{old_infor["TimeGap"].values[-1]} now in Targetfolder')
    _target_folder = baganalysis.bagresult.bagdata.target_folder
    shutil.copy(
        old_infor["Source_Path"].values[-1],
        os.path.join(_target_folder, str(old_infor["TimeGap"].values[-1]) + ".csv"),
    )
    # update bagresult.datadict
    new_df = pd.read_csv(old_infor["Source_Path"].values[-1])
    new_time = old_infor["TimeGap"].values[-1]
    baganalysis.bagresult.datadict.update({new_time: new_df})
    # update bagresult.interpolatefunct_dict
    df = new_df
    tem_x = np.array([df["Frequency(ppm)"]]).flatten()
    tem_y = np.array([df["Intensity"]]).flatten()
    tem_f = interp1d(tem_x, tem_y, kind="cubic")

    baganalysis.bagresult.interpolatefunct_dict.update({new_time: tem_f})
    # update bagresult.plotdata_df
    old_plotdata_df = baganalysis.bagresult.plotdata_df
    baganalysis.bagresult.plotdata_df[new_time] = tem_f(
        old_plotdata_df["Frequency"].values
    )

    baganalysis.bagresult.save_processdata()

    # update baganalysis.analysis_df

    new_analysisdf = update_newanalysis(tem_f, new_time, baganalysis)
    print(new_analysisdf)
    temanalysis_df = baganalysis.analysis_df.append(new_analysisdf).reset_index(
        drop=True
    )
    baganalysis.analysis_df = temanalysis_df
    # print(baganalysis.analysis_df)
    baganalysis.save_processdata()


def update_bagdata(bagdata: preprocess.Bag_data, event):
    root = os.path.split(event.src_path)[0]
    start_time = preprocess.get_name_start_time(root)
    old_infor = pd.read_csv(bagdata.information)
    if len(old_infor) == 0:
        new_timegap = 0
    else:
        tem_timegap = (
            start_time - pd.to_datetime(np.min(old_infor["DateTime"]))
        ).total_seconds()
        new_timegap = int(np.floor(tem_timegap))

    data_newinfor = np.asarray([start_time, event.src_path, new_timegap]).reshape(
        (1, 3)
    )
    newinfor_df = pd.DataFrame(data_newinfor, columns=list(old_infor.columns))
    infor_df = old_infor.append(newinfor_df).reset_index(drop=True)
    infor_df.to_csv(bagdata.information, index=False)
