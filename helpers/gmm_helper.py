# -*- coding: utf-8 -*-
from .shared_imports import *


def create_gmm_config(bandwidth, fitting_range, fit_limit, bin_width, kde_kernel='gaussian', fit_method='square_error'):
    config = {'bandwidth': bandwidth,
              'fitting_range': fitting_range,
              'fit_limit': fit_limit,
              'bin_width': bin_width,
              'kde_kernel': kde_kernel,
              'fit_method': fit_method}
    return config


def group_gmm_param_from_gmm_param_array(gmm_param_array, sort_group=True):
    from operator import itemgetter
    from .app_helper import chunks
    # from 17-1 -> 6-n array
    gmm = list(chunks(gmm_param_array, 6))
    if sort_group:
        gmm = sorted(gmm, key=itemgetter(0), reverse=True)  # reorder by fraction, from big to small
    return gmm


# GMM result
def read_gmm_em_result(clf):
    gmm_em_result = []
    for i in range(clf.n_components):
        weight = clf.weights_[i]
        meanx, meany = clf.means_[i].tolist()
        sigx, sigy = np.sqrt(clf.covariances_[i][0, 0]), np.sqrt(clf.covariances_[i][1, 1])
        rho = clf.covariances_[i][0, 1]/(sigx*sigy)
        gaussian_params = weight, meanx, meany, sigx, sigy, rho
        gmm_em_result.extend(gaussian_params)
    return gmm_em_result


def create_gaussian_2d(meanx, meany, sigx, sigy, rho):
    from scipy.stats import multivariate_normal
    sigxy = rho*sigx*sigy
    return multivariate_normal(mean=[meanx, meany], cov=[[sigx**2, sigxy], [sigxy, sigy**2]],
                               allow_singular=True)


def generate_gmm_pdf_from_grouped_gmm_param(gmm):
    gaussian_group = []
    for gaussian_param in gmm:
        f, u, v, sigu, sigv, rho = gaussian_param
        g = create_gaussian_2d(u, v, sigu, sigv, rho)
        gaussian_group.append([f, g])

    def mixed_model_pdf(points):
        result = 0
        for (f, g) in gaussian_group:
            result = result + f*g.pdf(points)
        return result
    return mixed_model_pdf


def width_height_ratio(g):
    sigx, sigy, sigxy = g[3], g[4], g[5]*g[3]*g[4]
    cov_matrix = np.matrix([[sigx**2, sigxy], [sigxy, sigy**2]])
    w, v = np.linalg.eigh(cov_matrix)
    a, b = np.sqrt(w[0]), np.sqrt(w[1])
    return a/b


def width_height_ratios_set(gmm):
    gmm = group_gmm_param_from_gmm_param_array(gmm, sort_group=False)
    ratios_set = [width_height_ratio(g) for g in gmm]
    return np.asarray(ratios_set)


def fit_gmm(df, config, x0=None, number_of_gaussian=3):
    # Fit the GMM through KDE, EM and optimization
    # 根据KDE, EM以及优化算法求解GMM
    # 1. Create Input, speed_set
    # 1. 读入输入数据df和拟合设定参数config
    sample = array(list(zip(df.x, df.y)))
    bandwidth, points, kde_kernel, fit_limit, fit_method = \
        config['bandwidth'], config['fitting_range'], \
        config['kde_kernel'], config['fit_limit'], config['fit_method']

    # 2. KDE + EM fitting
    # 2. 拟合经验分布，求解EM算法下的GMM，作为下一步优化求解的初值
    kde = neighbors.KernelDensity(bandwidth=bandwidth, kernel=kde_kernel).fit(sample)
    kde_result = exp(kde.score_samples(points))
    if not x0:
        clf = mixture.GaussianMixture(n_components=number_of_gaussian, covariance_type='full')
        clf.fit(sample)
        x0 = gmm_em_result = read_gmm_em_result(clf)
        # x0 = [0.3333, 1, 1, 1, 1, 0.5,
        #  0.3333, 1, 1, 1, 1, 0.5,
        #  0.3333, 1, 1, 1, 1, 0.5]

    # 3. GMM fitting
    # 3. 使用优化算法求解GMM
    bonds = [(0., 0.99),(-fit_limit, fit_limit),
             (-fit_limit, fit_limit),(0., fit_limit),(0., fit_limit),(-0.99, 0.99)]*int(len(x0)/6)
    cons = [{'type': 'eq', 'fun': lambda x: sum(x[::6]) - 1},
#             {'type': 'ineq', 'fun': lambda x: width_height_ratios_set(x) - 1/3},
#             {'type': 'ineq', 'fun': lambda x: 3 - width_height_ratios_set(x)},
           ]
    result = sp.optimize.minimize(
        lambda x0: gmm_fit_score(x0, kde_result, points, method=fit_method),
        x0,
        bounds=bonds,
        constraints=cons,
        tol=0.000000000001,
        options={"maxiter": 500})

    # 4. Returns
    # 4. 返回结果，包括GMM的参数，概率密度函数等
    gmm_params = group_gmm_param_from_gmm_param_array(result.x)
    mixed_model_pdf = generate_gmm_pdf_from_grouped_gmm_param(gmm_params)
    gmm_pdf_result = mixed_model_pdf(points)
    return {
        'gmm': gmm_params,
        'kde_clf': kde,
        'kde_result': kde_result,
        'gmm_pdf_result': gmm_pdf_result,
        'number_of_iteration': result.nit,
    }


def gmm_fit_score(gmm, kde_result, points, method='square_error'):
    from .app_helper import cdf_from_pdf
    # Definition of the score for GMM fitting
    # 定义优化求解时，采用的目标函数
    # 1. Create the GMM PDF
    # 1. 根据GMM参数建立概率密度函数pdf
    if not isinstance(gmm[0], np.ndarray):
        gmm = group_gmm_param_from_gmm_param_array(gmm, sort_group=False)
    mixed_model_pdf = generate_gmm_pdf_from_grouped_gmm_param(gmm)
    # 2. Fit the model using different metrics
    # 2. 计算不同的拟合优度参数用于优化求解
    gmm_pdf_result = mixed_model_pdf(points)
    if method == 'square_error':
        # 2.1 Square error
        error_array = power(gmm_pdf_result - kde_result, 2)
        result = mse_log = log(np.average(error_array))
    elif method == 'chi_square':
        # 2.2 Normalized Chi square
        error_array = power(gmm_pdf_result - kde_result, 2)
        result = chi_square = log(sum(error_array/gmm_pdf_result))
    elif method == 'k_s':
        # 2.3 K-S
        gmm_cdf = cdf_from_pdf(gmm_pdf_result)
        kde_cdf = cdf_from_pdf(kde_result)
        diff = abs(gmm_cdf - kde_cdf)
        result = KS = log(np.amax(diff))
    return result


def bandwidth_selection(df, knot_unit, kde_kernel='gaussian'):
    from sklearn.model_selection import GridSearchCV
    from .plot_print_helper import plt_configure
    # Grid search for KDE bandwidth
    # 使用Grid search求解KDE bandwidth值
    # 1. Init search range
    # 1. 根据网格大小确定初始搜索范围
    if knot_unit:
        bandwidth_range = arange(0.7, 2, 0.2)
    else:
        bandwidth_range = arange(0.3, 1.2, 0.1)

    # 2. Data prep
    # Grid search is unable to deal with too many data (a long time is needed)
    # 2. 对数据做相应准备。如果数据量过大，KDE速度非常慢，因此通过随机抽样限定gridsearch使用数据的大小
    if len(df) > 50000:
        df_resampled = df.sample(n=50000, replace=True)
        # bandwidth_search_sample = array(list(zip(df_resampled.x, df_resampled.y)))
        bandwidth_search_sample = np.column_stack((df_resampled.x, df_resampled.y))
    else:
        bandwidth_search_sample = np.column_stack((df.x, df.y))

    # 3. Grid search and obtain bandwidth result
    # 3. 使用Grid search求解KDE Bandwidth
    grid = GridSearchCV(neighbors.KernelDensity(kernel=kde_kernel),
                        {'bandwidth': bandwidth_range}, n_jobs=-1, cv=4, return_train_score=False)
    grid.fit(bandwidth_search_sample)
    bandwidth = grid.best_params_['bandwidth']

    # 4. Create Data Viz
    # 4. 绘制图表以供检验结果
    fig, ax = plt.subplots()
    ax.plot(bandwidth_range, grid.cv_results_['mean_test_score'], label='test')
    ax.fill_between(bandwidth_range,
                     grid.cv_results_['mean_test_score'] + grid.cv_results_['std_test_score'],
                     grid.cv_results_['mean_test_score'] - grid.cv_results_['std_test_score'], alpha=0.2)
    plt_configure(figsize=(4, 3))
    plt.close()

    return bandwidth, fig


def gmm_marginal_distribution(f, x, rads=linspace(0, 2*pi, num=36+1), bin_width=1):
    from scipy import integrate
    density_speed_expected_gmm = array([integrate.nquad(f, [[x_, x_+bin_width], [0, 2*pi]])
                                        for x_ in x[:-1]])[:, 0]
    y_cdf_gmm = array([integrate.nquad(f, [[0, x_val], [0, 2*pi]])
                       for x_val in x])[:, 0]
    density_dir_expected = array([integrate.nquad(f, [[0, inf], [x_-pi/36, x_+pi/36]])
                                  for x_ in rads])[:, 0]
    return x, rads, density_speed_expected_gmm, y_cdf_gmm, density_dir_expected


def gmm_integration_in_direction(f, start_radian, end_radian, bins, bin_width=1):
    from scipy import integrate
    direction_prob = integrate.nquad(f, [[0, inf], [start_radian, end_radian]])[0]
    y_gmm_ = array([integrate.nquad(f, [[x_, x_ + bin_width], [start_radian, end_radian]])
        for x_ in bins[:-1]])[:, 0]
    y_gmm = y_gmm_/direction_prob/bin_width

    y_cdf_gmm = array([integrate.nquad(f, [[0, x_], [start_radian, end_radian]])
         for x_ in bins])[:, 0]/direction_prob
    return bins, y_gmm, y_cdf_gmm, direction_prob


def gmm_univar_gof(df_standard, gmm_params, x, bin_width):
    from .app_helper import empirical_marginal_distribution, sector_r_square
    mixed_model_pdf = generate_gmm_pdf_from_grouped_gmm_param(gmm_params)
    def f_gmm(V, theta):
        return (mixed_model_pdf([[V * cos(theta), V * sin(theta)]])) * V

    _, _, density, y_ecdf, density_dir = empirical_marginal_distribution(df_standard, x)
    _, _, density_speed_expected_gmm, y_cdf_gmm, density_dir_expected = gmm_marginal_distribution(f_gmm, x,
                                                                                                  bin_width=bin_width)
    r_square = sector_r_square(density * bin_width, density_speed_expected_gmm)
    k_s = max(np.abs(y_cdf_gmm - y_ecdf))
    r_square_dir = sector_r_square(density_dir * 10, density_dir_expected[:-1])

    return {'r_square': r_square, 'k_s': k_s, 'r_square_dir': r_square_dir}
