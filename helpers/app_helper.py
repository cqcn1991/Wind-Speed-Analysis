import numpy as np

def R_square_of(MSE, kde_result):
    # R square measure:
    # https://en.wikipedia.org/wiki/Coefficient_of_determination
    y_mean = np.mean(kde_result)
    SS_tot = np.power(kde_result - y_mean,2)
    SS_tot_avg = np.average(SS_tot)

    SS_res_avg = MSE
    R_square = 1 - SS_res_avg/SS_tot_avg

    return R_square