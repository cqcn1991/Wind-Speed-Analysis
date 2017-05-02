from .shared_imports import *


def fit_per_fold(df, train_index, test_index, fit_method, number_of_gaussian, config):
    from .gmm_helper import fit_gmm
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
    from .gmm_helper import fit_gmm
    df_resampled = df.sample(frac=1, replace=True)
    result = fit_gmm(df_resampled, fit_method=fit_method,
                     config=config, number_of_gaussian=gaussian_number)
    return result


def resampled_kde(df, kde_result, config):
    from .app_helper import goodness_of_fit_summary
    bandwidth, points, kde_kernel = config['bandwidth'], config['fitting_range'], config['kde_kernel']
    df_resampled = df.sample(frac=1, replace=True)
    speed_resampled = array(list(zip(df_resampled.x, df_resampled.y)))
    kde2 = neighbors.KernelDensity(bandwidth=bandwidth, kernel=kde_kernel).fit(speed_resampled)
    kde_result2 = exp(kde2.score_samples(points))
    return goodness_of_fit_summary(kde_result2, kde_result)


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

    bin_width = 1
    bins = arange(0, sub_df.speed.max()+bin_width, bin_width)

    density_, division = np.histogram(sub_df['speed'], bins=bins)
    density = density_/len(df)
    density_expected_ =[sp.integrate.nquad(f, [[x_, x_+bin_width], [angle_radian-incre_radian/2, angle_radian+incre_radian/2]])
                        for x_ in bins[:-1]]
    density_expected = array(list(zip(*density_expected_ ))[0])
    curves = {'angle': angle, 'data_size': data_size, 'max_speed': sub_df.speed.max(),
              'density': density, 'density_expected': density_expected}
    return curves


def direction_compare2(gmm, df, angle, incre, complex=False):
    from .app_helper import select_df_by_angle, fit_weibull_and_ecdf
    from .gmm_helper import generate_gmm_pdf_from_grouped_gmm_param, gmm_integration_in_direction
    from .post_process import sector_r_square
    mixed_model_pdf = generate_gmm_pdf_from_grouped_gmm_param(gmm)

    def f(V, theta):
        return (mixed_model_pdf([[V * cos(theta), V * sin(theta)]])) * V

    angle_radian, incre_radian = radians(angle), radians(incre)
    start_angle, end_angle = angle-incre/2, angle+incre/2

    # 0. Select data from observation
    sub_df, sub_max_speed = select_df_by_angle(df, start_angle, end_angle)
    data_size = len(sub_df.speed)

    bin_width = 1
    bins = arange(0, sub_df.speed.max()+bin_width, bin_width)
    density_, _ = np.histogram(sub_df['speed'], bins=bins)
    density = density_/len(df)

    density_expected_gmm_ = [sp.integrate.nquad(f, [[x_, x_ + 1], [angle_radian - incre_radian / 2, angle_radian + incre_radian / 2]])
                             for x_ in bins[:-1]]
    density_expected_gmm = array(list(zip(*density_expected_gmm_))[0])

    fig = plt.figure()
    ax = fig.add_subplot(111)
    x=arange(1,10)
    ax.plot(x, x*angle)

    if complex:
        # 1. Get Weibull and ECDF
        x, y_weibull, y_cdf_weibull, weibull_params, y_ecdf = fit_weibull_and_ecdf(sub_df.speed)
        # 2. Get GMM PDF, CDF
        _, y_gmm, y_cdf_gmm, direction_prob = gmm_integration_in_direction(f, angle_radian - incre_radian / 2,
                                                                           angle_radian + incre_radian / 2, x)

        # 3. R square for GMM, Weibull at each direction
        R_square_gmm = sector_r_square(density, density_expected_gmm/direction_prob) # adjusting for each direction
        density_expected_weibull = sp.stats.weibull_min.cdf(bins[1:], *weibull_params) - sp.stats.weibull_min.cdf(bins[:-1], *weibull_params)
        R_square_weibull = sector_r_square(density, density_expected_weibull)

        # 4. K-S for GMM, Weibull
        cdf_diff, cdf_diff_weibull = np.abs(y_ecdf - y_cdf_gmm), np.abs(y_ecdf - y_cdf_weibull)


        curves = {'angle': angle, 'direction': angle, 'datasize': data_size, 'weight': direction_prob, 'x': x,
                  'gmm_pdf': y_gmm, 'gmm_cdf': y_cdf_gmm,
                  'weibull_pdf': y_weibull, 'weibull_cdf': y_cdf_weibull, 'ecdf': y_ecdf,
                  'max_cdf_diff_gmm': cdf_diff.max(), 'max_cdf_diff_weibull': cdf_diff_weibull.max(),
                  'r_square_gmm': R_square_gmm, 'r_square_weibull': R_square_weibull}

    else:
        curves = {'angle': angle, 'data_size': data_size, 'max_speed': sub_df.speed.max(),
                  'density': density, 'density_expected': density_expected_gmm, 'fig': fig}

    return curves


def try_plot(y):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    x=arange(1,10)
    ax.plot(x, x*y)
    return fig



