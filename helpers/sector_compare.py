from __future__ import division
from .shared_imports import *


def x_compare(y_ecdf, y_cdf_gmm, y_cdf_weibull, x):
    x_gmm = np.interp(y_ecdf, y_cdf_gmm, x)
    x_weibull = np.interp(y_ecdf, y_cdf_weibull, x)
    diff_x = np.divide(x_gmm[1:] - x[1:], x[1:])
    diff_x_weibull = np.divide(x_weibull[1:] - x[1:], x[1:])
    diff_x_df = pd.DataFrame({'y_ecdf': y_ecdf[1:], 'x': x[1:], 'x_gmm': x_gmm[1:],
                          'x_weibull': x_weibull[1:], 'diff_x': diff_x, 'diff_x_weibull': diff_x_weibull})
    diff_x_df = diff_x_df.query("(y_ecdf <= 0.95) & (y_ecdf >= 0.5)")
    return diff_x_df


def sector_r_square(density, density_expected):
    y_mean = np.mean(density)
    SS_tot = np.sum(np.power(density - y_mean, 2))
    SS_res = np.sum(np.power(density - density_expected, 2))
    R_square = 1 - SS_res / SS_tot
    return R_square


def nominal_avg_and_weight_avg(df_weight, df_value):
    return np.average(df_value), np.sum(df_weight / df_weight.sum() * df_value)


def plot_sectoral_comparison(gmm, weibull, direction, datasize):
    from .plot_print_helper import plt_configure
    _, gmm_mean = nominal_avg_and_weight_avg(datasize, gmm)
    _, weibull_mean = nominal_avg_and_weight_avg(datasize, weibull)

    line, = plt.plot(direction, gmm, '-', label = 'GMM', marker='o')
    plt.axhline(gmm_mean, linestyle='--', color = line.get_color(), label ='GMM weighted average')

    line,= plt.plot(direction, weibull, '-', label = 'Weibull', marker='o')
    plt.axhline(weibull_mean, linestyle='--', color = line.get_color(), label ='Weibull weighted average')
    plt_configure(xlabel='Direction',
                  legend={'loc':'best'},figsize=(4.5, 2.5))
    plt.locator_params(axis='y', nbins=5)
    return gmm_mean, weibull_mean