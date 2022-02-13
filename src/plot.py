"""
make plot to see the changes in intensity with time
van de la moi lan do lai co mot frequency khac nhau gay kho khan
cho viec plot
cung voi do la thieu gia tri cua intensity cho 3d plot
- co dinh 1 intervall cho ppm (-26:36: 65535)
tu -26 den 36 va gom 65535 diem
- dung ppm la row index cho df
- moi lan do se tao them 1 cot
dung time lam col index
cach tao col moi la dung interpol de tao gia tri

"""

# %%

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import src.store_results as store_results
import warnings

warnings.filterwarnings("ignore")
# %%
"""
viet function cho input df  output f() interpolate

"""

######################


def plot_3D(
    bag_result: store_results.Bag_result,
    timestr=0,
    timeend=100 ** 100,
    ppmstr=-27,
    ppmend=37,
    view_op1=10,
    view_op2=30,
):
    data_df = bag_result.make_plot_data()
    timestr, timeend = timestr * 3600, timeend * 3600
    tem_df = store_results.filter_datadf(data_df, timestr, timeend, ppmstr, ppmend)
    x = [i for i in list(tem_df.columns) if i != "Frequency"]  # time
    x_h = np.asarray(x) / 3600
    y = tem_df["Frequency"]  # ppm
    X, Y = np.meshgrid(x_h, y)
    Z = np.matrix(tem_df[x])  # intensity
    # create figure
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"}, dpi=200)
    fig.set_size_inches(16, 9)
    surf = ax.plot_surface(
        X, Y, Z, cmap=cm.coolwarm, linewidth=0, alpha=1, antialiased=True
    )
    fig.colorbar(surf, shrink=0.5, aspect=5)
    ax.set_xlabel("time")
    ax.set_ylabel("Frequency(ppm)")
    ax.set_zlabel("Intensity")
    ax.view_init(view_op1, view_op2)
    plt.show()
    result_list = [fig, tem_df]
    return result_list


def plot_2d(
    bag_result: store_results.Bag_result,
    timestr=0,
    timeend=100 ** 100,
    ppmstr=-27,
    ppmend=37,
    plot_option="ppm",
):
    """
    make 2D plot
    - ppm- intensity
    - time - intensity
    """
    data_df = bag_result.make_plot_data()
    timestr, timeend = timestr * 3600, timeend * 3600
    tem_df = store_results.filter_datadf(data_df, timestr, timeend, ppmstr, ppmend)
    tem_df = tem_df.reset_index(drop=True)
    x = [i for i in list(tem_df.columns) if i != "Frequency"]  # time
    x_h = np.asarray(x) / 3600
    y = tem_df["Frequency"]  # ppm
    fig, ax = plt.subplots(dpi=200)
    fig.set_size_inches(16, 9)
    if plot_option == "ppm":
        for i in x:
            ax.plot(y, tem_df[i], color="black", alpha=0.15, linewidth=0.95)
        ax.invert_xaxis()
        plt.xlabel("chemical shift(ppm) ")
        plt.ylabel("amplitude")
        plt.show()
    else:
        for i in range(len(tem_df)):
            ax.plot(
                x_h, tem_df.loc[i, :].values[1:], label=f"{tem_df.loc[i,:].values[0]}"
            )
        ax.invert_xaxis()
        plt.xlabel("time(h)")
        plt.ylabel("amplitude")
        plt.show()
        print(y)
    result_list = [fig, tem_df]
    return result_list
