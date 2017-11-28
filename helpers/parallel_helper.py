from .shared_imports import *


def fit_per_fold(df, train_index, test_index, fit_method, number_of_gaussian, config):
    from .gmm_helper import fit_gmm
    from .app_helper import goodness_of_fit_summary
    bandwidth, points, kde_kernel, bin_width = config['bandwidth'], config['fitting_range'], config['kde_kernel'], config['bin_width']
    sub_df, sub_df_test = df.iloc[train_index], df.iloc[test_index]

    # 1. Train
    result = fit_gmm(sub_df, config=config, number_of_gaussian=number_of_gaussian)
    gmm_pdf_result_train = result['gmm_pdf_result']
    kde_result_train = result['kde_result']

    # 2. Validate
    # GMM from Train - KDE from Test
    sample = array(list(zip(sub_df_test.x, sub_df_test.y)))
    kde_test = neighbors.KernelDensity(bandwidth=bandwidth).fit(sample)
    kde_result_test = exp(kde_test.score_samples(points))

    gof_train = goodness_of_fit_summary(gmm_pdf_result_train, kde_result_train, bin_width)
    gof_test = goodness_of_fit_summary(gmm_pdf_result_train, kde_result_test, bin_width)
    return gof_train, gof_test


def resampled_fitting(df, gaussian_number, config):
    from .gmm_helper import fit_gmm
    df_resampled = df.sample(frac=1, replace=True)
    result = fit_gmm(df_resampled, number_of_gaussian=gaussian_number,
                     config=config)
    return result


def resampled_kde(df, kde_result, config):
    from .app_helper import goodness_of_fit_summary, fit_kde
    df_resampled = df.sample(frac=1, replace=True)
    kde_result2, _ = fit_kde(df_resampled, config)
    return goodness_of_fit_summary(kde_result2, kde_result, config['bin_width'])


def kde_gofs(df_previous,  kde_result_standard, config):
    from .app_helper import goodness_of_fit_summary, fit_kde
    kde_result2, _ = fit_kde(df_previous, config)
    return goodness_of_fit_summary(kde_result2, kde_result_standard, config['bin_width'])


def univar_gof(df_previous, density, y_ecdf, x, density_dir):
    from .app_helper import empirical_marginal_distribution, sector_r_square
    _, _, density_expected, y_ecdf_previous, density_dir_expected = empirical_marginal_distribution(df_previous, x)

    # 1. Speed
    r_square = sector_r_square(density, density_expected)
    k_s = max(np.abs(y_ecdf - y_ecdf_previous))

    # 2. Direction
    r_square_dir = sector_r_square(density_dir, density_dir_expected)
    return {'r_square': r_square, 'k_s': k_s, 'r_square_dir': r_square_dir}


def gmm_gofs_in_previous(df_previous, gmm_pdf_result, config):
    from .app_helper import goodness_of_fit_summary, fit_kde
    kde_result_previous, _ = fit_kde(df_previous, config)
    return goodness_of_fit_summary(gmm_pdf_result, kde_result_previous, config['bin_width'])


def sub_df_at_angle(df, angle, incre, bin_width):
    from .app_helper import select_df_by_angle
    start_angle, end_angle = angle-incre/2, angle+incre/2
    start_radian, end_radian = np.radians([start_angle, end_angle])
    sub_df, sub_max_speed = select_df_by_angle(df, start_angle, end_angle)
    data_size = len(sub_df.speed)
    bins = arange(0, sub_max_speed + bin_width, bin_width)
    return sub_df, bins, start_radian, end_radian, data_size


def base_direction_compare(df, angle, incre, bin_width=1):
    sub_df, bins, start_radian, end_radian, data_size = sub_df_at_angle(df, angle, incre, bin_width)
    density_, division = np.histogram(sub_df['speed'], bins=bins)
    density = density_/len(df)
    curves = {'angle': angle, 'data_size': data_size, 'max_speed': sub_df.speed.max(),
              'density': density,}
    return curves


def direction_compare(gmm, df, angle, incre, bin_width=1):
    from .gmm_helper import generate_gmm_pdf_from_grouped_gmm_param
    sub_df, bins, start_radian, end_radian, data_size = sub_df_at_angle(df, angle, incre, bin_width)
    density_, division = np.histogram(sub_df['speed'], bins=bins)
    density = density_/len(df)

    mixed_model_pdf = generate_gmm_pdf_from_grouped_gmm_param(gmm)
    def f(V, theta):
        return (mixed_model_pdf([[V * cos(theta), V * sin(theta)]])) * V
    density_expected = array([integrate.nquad(f, [[x_, x_+bin_width], [start_radian, end_radian]])
                              for x_ in bins[:-1]])[:, 0]

    curves = {'angle': angle, 'data_size': data_size, 'max_speed': sub_df.speed.max(),
              'density': density, 'density_expected': density_expected}
    return curves


def emp_direction_compare(df_previous, df, angle, incre, bin_width=1):
    from .app_helper import select_df_by_angle
    sub_df, bins, start_radian, end_radian, data_size = sub_df_at_angle(df, angle, incre, bin_width)
    density_, division = np.histogram(sub_df['speed'], bins=bins)
    density = density_/len(df)

    sub_df_previous, _ = select_df_by_angle(df_previous, angle-incre/2, angle+incre/2)
    density_expected_, division = np.histogram(sub_df_previous['speed'], bins=bins)
    density_expected = density_expected_ / len(df_previous)

    curves = {'angle': angle, 'data_size': data_size, 'max_speed': sub_df.speed.max(),
              'density': density, 'density_expected': density_expected}
    return curves


def al_direction_compare(al_params, df, angle, incre, bin_width=1):
    from .angular_linear import generate_al_pdf_from
    sub_df, bins, start_radian, end_radian, data_size = sub_df_at_angle(df, angle, incre, bin_width)
    density_, division = np.histogram(sub_df['speed'], bins=bins)
    density = density_/len(df)

    speed_params, vonmises_params, connection_params = al_params
    f_al = generate_al_pdf_from(speed_params, vonmises_params, connection_params)
    density_expected_al = array([integrate.nquad(f_al, [[x_, x_ + bin_width], [start_radian, end_radian]])
                                 for x_ in bins[:-1]])[:, 0]

    curves = {'angle': angle, 'data_size': data_size, 'max_speed': sub_df.speed.max(),
              'density': density, 'density_expected': density_expected_al}
    return curves


def gmm_weibull_empirical_direction(gmm, df, angle, incre, bin_width=1):
    from .gmm_helper import generate_gmm_pdf_from_grouped_gmm_param, gmm_integration_in_direction
    from .app_helper import fit_weibull_and_ecdf
    sub_df, bins, start_radian, end_radian, _ = sub_df_at_angle(df, angle, incre, bin_width)

    density, _ = np.histogram(sub_df['speed'], bins=bins, density=True)
    _, y_weibull, density_expected_weibull, y_cdf_weibull, _, y_ecdf = fit_weibull_and_ecdf(sub_df.speed, bins)

    mixed_model_pdf = generate_gmm_pdf_from_grouped_gmm_param(gmm)
    def f(V, theta):
        return (mixed_model_pdf([[V * cos(theta), V * sin(theta)]])) * V
    _, y_gmm, y_cdf_gmm, direction_prob = gmm_integration_in_direction(f, start_radian, end_radian, bins, bin_width)

    curves = {'angle': angle,  'bins': bins, 'y_ecdf': y_ecdf, 'density': density,
              'y_weibull': y_weibull, 'density_expected_weibull': density_expected_weibull, 'y_cdf_weibull': y_cdf_weibull,
              'density_expected_gmm': y_gmm, 'y_cdf_gmm': y_cdf_gmm, 'direction_prob': direction_prob}
    return curves


def al_direction(al_params, df, angle, incre, bin_width=1):
    from .angular_linear import generate_al_pdf_from, al_integration_in_direction
    sub_df, bins, start_radian, end_radian, _ = sub_df_at_angle(df, angle, incre, bin_width)
    speed_params, dir_params, connection_params = al_params
    f_al = generate_al_pdf_from(speed_params, dir_params, connection_params)
    _, density_expected, y_cdf, direction_prob = al_integration_in_direction(f_al, start_radian,
                                                                                 end_radian, bins, bin_width)

    curves = {'angle': angle,
              'y_al': density_expected, 'y_cdf_al': y_cdf, 'direction_prob': direction_prob }
    return curves


def gmm_cv_time(df_all_years, start_year, year_length, x, config, NUMBER_OF_GAUSSIAN):
    from .gmm_helper import fit_gmm, gmm_univar_gof
    current_df = df_all_years[str(start_year):str(start_year+year_length-1)]
    result = fit_gmm(current_df, config=config, number_of_gaussian=NUMBER_OF_GAUSSIAN)
    train_gof = gmm_univar_gof(current_df, result['gmm'],  x, config['bin_width'])
    # 2. Validated on later dataset, 2001-2010
    new_df = df_all_years[str(start_year+year_length):str(start_year+2*year_length-1)]
    test_gof = gmm_univar_gof(new_df, result['gmm'],  x, config['bin_width'])
    return train_gof, test_gof




