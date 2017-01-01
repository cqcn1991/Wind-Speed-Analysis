from __future__ import division
from .shared_imports import *


def myfunc(x):
    from math import sqrt
    return sqrt(x)


def fit_per_fold(df, train_index, test_index, fit_method, number_of_gaussian, config):
    from .core import fit_gmm
    from .app_helper import goodness_of_fit_summary
    bandwidth, points, kde_kernel = config['bandwidth'], config['fitting_range'], config['kde_kernel']
    sub_df, sub_df_test = df.iloc[train_index], df.iloc[test_index]

    # 1. Train
    result = fit_gmm(sub_df, fit_method=fit_method,
                     config=config, number_of_gaussian=number_of_gaussian)
    gmm_pdf_result_train = result['gmm_pdf_result']
    kde_result_train = result['kde_result']

    # 2. Validate
    # GMM from Train - KDE from Test
    sample = array(list(zip(sub_df_test.x, sub_df_test.y)))
    kde_test = neighbors.KernelDensity(bandwidth=bandwidth).fit(sample)
    kde_result_test = exp(kde_test.score_samples(points))

    gof_train = goodness_of_fit_summary(gmm_pdf_result_train, kde_result_train)
    gof_test = goodness_of_fit_summary(gmm_pdf_result_train, kde_result_test)
    return gof_train, gof_test


def resampled_fitting(df, fit_method, gaussian_number, config):
    from .core import fit_gmm
    df_resampled = df.sample(frac=1, replace=True)
    result = fit_gmm(df_resampled, fit_method=fit_method,
                     config=config, number_of_gaussian=gaussian_number)
    return result


def direction_compare(gmm, df, angle, incre):
    from .app_helper import select_df_by_angle
    from .gmm_helper import generate_gmm_pdf_from_grouped_gmm_param
    mixed_model_pdf = generate_gmm_pdf_from_grouped_gmm_param(gmm)
    def f(V, theta):
        return (mixed_model_pdf([[V * cos(theta), V * sin(theta)]])) * V

    angle_radian, incre_radian = radians(angle), radians(incre)
    start_angle, end_angle = angle-incre/2, angle+incre/2
    sub_df, sub_max_speed = select_df_by_angle(df, start_angle, end_angle)
    data_size = len(sub_df.speed)

    bins = arange(0, sub_df.speed.max()+1)

    density_, division = np.histogram(sub_df['speed'],bins=bins)
    density = density_/len(df)
    density_expected_ =[sp.integrate.nquad(f, [[x_, x_+1],[angle_radian-incre_radian/2, angle_radian+incre_radian/2]])
                        for x_ in bins[:-1]]
    density_expected = array(list(zip(*density_expected_ ))[0])
    curves = {'angle': angle, 'data_size': data_size, 'max_speed': sub_df.speed.max(),
          'density': density, 'density_expected': density_expected}
    return curves