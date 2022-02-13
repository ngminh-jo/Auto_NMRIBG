import src.peak_area  as peak_area
import src.store_results as store_results
import pathlib
import os
import pickle
import numpy as np
import pandas as pd

# %%


class Bag_analysis:
    def __init__(
        self,
        sty_const: float,
        c0_tmsp: float,
        bagresult: store_results.Bag_result,
        tmsp: peak_area.Chemical_shift,
        chemicals: list[peak_area.Chemical_shift],
        nameoption="",
    ) -> None:
        self.sty_const = sty_const
        self.c0_tmsp = c0_tmsp
        self.bagresult = bagresult
        self.tmsp = tmsp
        self.chemicals = chemicals
        self.nameoption = nameoption
        self.make_dir_analysis()
        self.analysis_df = self.make_analysisdf()
        self.save_processdata()

    def make_dir_analysis(self):
        _dir_ana = os.path.join(
            self.bagresult.analysis_results, "Bag_analysis" + self.nameoption
        )
        file = pathlib.Path(_dir_ana)
        if file.exists() == False:
            os.mkdir(_dir_ana)
        self.analysis_dir = _dir_ana

    def save(self):
        baganalysis_path = os.path.join(self.analysis_dir, "baganalysis.pkl")
        pickle.dump(self, open(baganalysis_path, "wb"))
        print(f"save {type(self)} in {baganalysis_path}")
        return baganalysis_path

    def save_processdata(self):
        save_data_in_baganalyis(self.analysis_df, self, "analysisdata")

    def make_analysisdf(self):
        return analysis_internal_standard_tmsp(
            self.sty_const, self.c0_tmsp, self.bagresult, self.tmsp, *self.chemicals
        )


# %%

# sty_const = Q*M/V


def analysis_internal_standard_tmsp(
    sty_const: float,
    c0_tmsp: float,
    bagresult: store_results.Bag_result,
    tmsp: peak_area.Chemical_shift,
    *args: list[peak_area.Chemical_shift],
):
    """
    Analysis with internal standard TMSP-d4: Compare chemical shift to internal standard
    """

    chemicals = (tmsp,) + args
    # peak area
    analysis_df = peak_area.compute_multiple_peak_area(bagresult, *(chemicals))
    # signal per proton
    for name in list(analysis_df.columns):
        for chemical in chemicals:
            if name == chemical.name:
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
    # more analysis methods can be added
    return analysis_df


# %%
def save_data_in_baganalyis(data, baganalysis: Bag_analysis, nameoption=str):
    if isinstance(data, dict):
        dict_path = os.path.join(baganalysis.analysis_dir, nameoption + ".npy")
        np.save(dict_path, data)
        # print(f"save {nameoption +'.npy'} in {dict_path}")
        # setattr(bagresult, nameoption, dict_path)
        return dict_path
    if isinstance(data, pd.DataFrame):
        df_path = os.path.join(baganalysis.analysis_dir, nameoption + ".csv")
        data.to_csv(df_path, index=False)
        # print(f"save {nameoption +'.csv'} in {df_path}")
        # setattr(bagresult, nameoption, df_path)
        return df_path


def load_baganalysis(baganalysis_path: os.path):
    file = pathlib.Path(baganalysis_path)
    if file.exists() == False:
        print(f"there is no bagdata object")
    else:
        return pickle.load(open(baganalysis_path, "rb"))
