from .shared_imports import *


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]


def dir_hist(df_dir, bins=arange(-5, 375, 10), density=False):
    density, bins = np.histogram(df_dir, bins=bins, density=density)
    density[0] = density[0] + density[-1]
    density = density[:-1]
    return density, bins


def get_lat_long(file_path):
    import os
    # Find stn file
    file_dir = file_path.rsplit('/', 1)[0] + '/'
    for file in os.listdir(file_dir):
        if file.endswith("stn.txt"):
            stn_file_path = file_dir + file
    # Get lat, lng
    with open(stn_file_path) as fp:
        for i, line in enumerate(fp):
            if i == 2:
                lat, long = line.split()[-3:-1]
    lat, long = float(lat), float(long)
    return lat, long


def myround(x, base=5):
    import math
    return int(base * math.floor(float(x)/base))


def sector_r_square(density, density_expected):
    # R square measure:
    # https://en.wikipedia.org/wiki/Coefficient_of_determination
    # Measures Model-Observation variance against Observation-Average variance
    y_mean = np.mean(density)
    SS_tot = np.sum(power(density - y_mean, 2))
    SS_res = np.sum(power(density - density_expected, 2))
    R_square = 1 - SS_res/SS_tot
    return R_square


def true_R_square(density_collection, datasize, params_num=24):
    densities = np.array([])
    densities_expected = np.array([])
    bin_num = 0
    for density_curves in density_collection:
        densities = np.concatenate([densities, density_curves['density']])
        densities_expected =  np.concatenate([densities_expected, density_curves['density_expected']])
        bin_num = bin_num + ceil(density_curves['max_speed'])
    y_mean = np.mean(densities)
    SS_tot = np.sum(np.power(densities - y_mean, 2))
    SS_res = np.sum(np.power(densities - densities_expected, 2))
    SS_tot_avg = SS_tot
    SS_res_avg = SS_res

    RMSE = sqrt(SS_res/bin_num)
    RRMSE = np.sum(power(1 - densities_expected, 2))
    MAE = np.sum(np.absolute(densities - densities_expected))/bin_num
    IA = 1 - SS_res/(np.sum(power(np.absolute(densities - y_mean) - np.absolute(densities_expected - y_mean), 2)))
    Chi_square = np.sum(power(1 - densities/densities_expected, 2))
    adjust_R_square = 1 - (SS_res/(bin_num-params_num-1))/(SS_tot/(bin_num-1))
    R_square = 1 - SS_res_avg / SS_tot_avg
    return RMSE*datasize, RRMSE, MAE*datasize, IA, Chi_square, adjust_R_square, R_square


def goodness_of_fit_summary(gmm_pdf_result, kde_result, bin_width):
    error_array = np.power(gmm_pdf_result - kde_result, 2)

    MSE = np.average(error_array)
    RMSE = np.sqrt(MSE)
    R_square = sector_r_square(kde_result, gmm_pdf_result)
    Chi_square = sum(error_array/gmm_pdf_result)
    Chi_square_2 = sum(power(kde_result/gmm_pdf_result-1, 2))

    gmm_cdf = cdf_from_pdf(gmm_pdf_result, bin_width)
    kde_cdf = cdf_from_pdf(kde_result, bin_width)
    diff = abs(gmm_cdf - kde_cdf)
    KS_stat = np.amax(diff)

    return {
        'MSE': MSE,
        'R_square': R_square,
        'Chi_square': Chi_square,
        'Chi_square_2': Chi_square_2,
        'K_S': KS_stat,
        'RMSE / Max': RMSE/np.max(kde_result),
        'RMSE / Mean': RMSE/np.mean(kde_result),
    }


def cdf_from_pdf(pdf, bin_width=1):
    if not isinstance(pdf[0], np.ndarray):
        original_dim = int(np.sqrt(len(pdf)))
        pdf = pdf.reshape(original_dim, original_dim)
    cdf = np.copy(pdf)
    xdim, ydim = cdf.shape
    for i in range(1, xdim):
        cdf[i,0] = cdf[i-1,0] + cdf[i,0]
    for i in range(1, ydim):
        cdf[0,i] = cdf[0,i-1] + cdf[0,i]
    for j in range(1, ydim):
        for i in range(1, xdim):
            cdf[i,j] = cdf[i-1,j] + cdf[i,j-1] - cdf[i-1,j-1] + pdf[i,j]
    return cdf*(bin_width**2)


def select_df_by_angle(df, start_angle, end_angle):
    start_angle, end_angle = start_angle%360, end_angle%360
    if start_angle > end_angle:
        sub_df = df.query('(dir >= @start_angle) & (dir <= 360)|(dir >= 0) & (dir <= @end_angle)')
    else:
        sub_df = df.query('(dir >= @start_angle) & (dir < @end_angle)')
    sub_max_speed = sub_df.speed.max()

    return sub_df, sub_max_speed


def max_count_for_histogram(data):
    count, div = np.histogram(data, bins=np.arange(0, data.max()))
    max_count = count.max()
    return max_count


def max_count_for_angles(df, start, end, incre):
    max_count_group = []
    for angle in arange(start, end, incre):
        start_angle, end_angle = angle-incre/2, angle+incre/2
        sub_df, sub_max_speed = select_df_by_angle(df, start_angle, end_angle)
        sub_max_count = max_count_for_histogram(sub_df.speed)
        max_count_group.append(sub_max_count)
    return max(max_count_group)


def generate_mean_std_gof(gof_result_groups):
    mean_gof_all = []
    std_gof_all = []
    for gof_group in gof_result_groups:
        df = pd.DataFrame(gof_group)
        mean_gof = np.mean(df)
        std_gof = np.std(df)
        mean_gof_all.append(mean_gof)
        std_gof_all.append(std_gof)
    mean_gof_df, std_gof_df = pd.DataFrame(mean_gof_all), pd.DataFrame(std_gof_all)
    mean_gof_df.index += 1
    std_gof_df.index += 1
    return mean_gof_df, std_gof_df


def get_location_name(file_path):
    file_name = file_path.split('/')[-1]
    location_name = file_path.split('/')[-2]
    return location_name


def generate_Z_from_X_Y(X,Y, Z_func):
    XX, YY=np.meshgrid(X,Y)
    coords=np.array((XX.ravel(), YY.ravel())).T
    Z = Z_func(coords).reshape(XX.shape)
    return Z


def fit_kde(df, config):
    bandwidth, points, kde_kernel = config['bandwidth'], config['fitting_range'], config['kde_kernel']
    speed_ = array(list(zip(df.x, df.y)))
    kde = neighbors.KernelDensity(bandwidth=bandwidth, kernel=kde_kernel).fit(speed_)
    kde_result = exp(kde.score_samples(points))
    return kde_result, kde


def empirical_marginal_distribution(df, x, degs=arange(-5, 375, 10)):
    bins = x
    density_speed, _ = np.histogram(df['speed'], bins=bins, density=True)
    y_ecdf = sm.distributions.ECDF(df['speed'])(x)
    density_dir, _ = dir_hist(df['dir'], bins=degs, density=True)
    return x, degs, density_speed, y_ecdf, density_dir


def fit_weibull(df_speed, x, weibull_params=None):
    from scipy.stats import weibull_min
    if not weibull_params:
        k_shape, _, lamb_scale = weibull_params = weibull_min.fit(df_speed, loc=0)
    y_weibull = weibull_min.pdf(x, *weibull_params)
    density_expected_weibull = weibull_min.cdf(x[1:], *weibull_params) - weibull_min.cdf(x[:-1], *weibull_params)
    y_cdf_weibull = 1 - exp(-(x / lamb_scale) ** k_shape)
    return weibull_params, y_weibull, density_expected_weibull, y_cdf_weibull


def fit_weibull_and_ecdf(df_speed, x=None):
    from scipy.stats import weibull_min
    max_speed = df_speed.max()
    if x is None:
        x = linspace(0, max_speed, 20)
    # Fit Weibull, notice loc value 0 or not
    weibull_params, y_weibull, _, y_cdf_weibull = fit_weibull(df_speed, x)
    # Fit Ecdf
    y_ecdf = sm.distributions.ECDF(df_speed)(x)
    return x, y_weibull, y_cdf_weibull, weibull_params, y_ecdf


def R_square_for_speed(df_speed, f_gmm, weibull_params, f_gmm_em, bin_width=1):
    from scipy.stats import weibull_min
    bins = arange(0, df_speed.max()+bin_width, bin_width)
    density, _ = np.histogram(df_speed, bins=bins, density=True)

    density_expected_gmm_ = [sp.integrate.nquad(f_gmm, [[x_, x_+bin_width], [0, 2*pi]]) for x_ in bins[:-1]]
    density_expected_gmm = array(list(zip(*density_expected_gmm_))[0])
    R_square_gmm = sector_r_square(density*bin_width, density_expected_gmm)

    density_expected_gmm_em_ = [sp.integrate.nquad(f_gmm_em, [[x_, x_+bin_width], [0, 2*pi]]) for x_ in bins[:-1]]
    density_expected_gmm_em = array(list(zip(*density_expected_gmm_em_))[0])
    R_square_gmm_em = sector_r_square(density*bin_width, density_expected_gmm_em)

    density_expected_weibull = weibull_min.cdf(bins[1:], *weibull_params) - weibull_min.cdf(bins[:-1], *weibull_params)
    R_square_weibull = sector_r_square(density*bin_width, density_expected_weibull)

    return R_square_gmm, R_square_weibull, R_square_gmm_em


