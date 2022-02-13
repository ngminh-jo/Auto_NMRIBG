# %%
from unittest import result
import src.store_results as store_results
import numpy as np
from scipy.integrate import quad
import pandas as pd
from functools import reduce

# %%


class Chemical_shift:
    def __init__(self, name: str, nr_proton: float, ppmstr: float, ppmend: float):
        self.name = name
        self.ppmstr = ppmstr
        self.ppmend = ppmend
        self.nr_proton = nr_proton
        self.shilf_intervall = [ppmstr, ppmend]

    def peak_area(self, bagresult: store_results.Bag_result):
        peak_area_df = compute_single_peak_area(bagresult, self)
        return peak_area_df

    def __repr__(self) -> str:
        rep = "Chemical_shift(" + str(self.name) + ")"
        return rep


# %%


def compute_single_peak_area(
    bag_result: store_results.Bag_result, chemical_shift: Chemical_shift
) -> pd.DataFrame:
    """
    Develop fucntions for compute peaks size
    - take the interpolation_dict and frequency intervall as inputs.
    - Return df with col: frequency_intervall and row_index: time

    """
    interpolate_dict = bag_result.interpolatefunct_dict
    peak_area_dict = {}
    for time, f in interpolate_dict.items():
        peak_area = np.abs(quad(f, chemical_shift.ppmstr, chemical_shift.ppmend))
        peak_area_dict.update({time: peak_area[0] * 10})
    peak_area_df = pd.DataFrame(
        data=list(peak_area_dict.items()), columns=["Time", chemical_shift.name]
    )
    return peak_area_df


# %%


def compute_multiple_peak_area(
    bag_result: store_results.Bag_result, *args: list[Chemical_shift]
) -> pd.DataFrame:
    df_list = [
        compute_single_peak_area(bag_result, chemical) for chemical in list(args)
    ]
    peakarea_df = reduce(lambda df1, df2: pd.merge(df1, df2, on="Time"), df_list)
    return peakarea_df
