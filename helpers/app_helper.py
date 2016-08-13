from __future__ import division
from .shared_imports import *


def R_square_of(MSE, kde_result):
    # R square measure:
    # https://en.wikipedia.org/wiki/Coefficient_of_determination
    # Measures Model-Observation variance against Observation-Average variance
    y_mean = np.mean(kde_result)
    SS_tot = np.power(kde_result - y_mean,2)
    SS_tot_avg = np.average(SS_tot)

    SS_res_avg = MSE
    R_square = 1 - SS_res_avg/SS_tot_avg

    return R_square


def true_R_square(density_collection):
    densities = []
    densities_expected = []
    for density_curves in density_collection:
        densities.extend(density_curves['density'])
        densities_expected.extend(density_curves['density_expected'])
    y_mean = np.mean(densities)
    SS_tot = np.sum(np.power(densities - y_mean, 2))
    SS_res = np.sum(np.power(np.asarray(densities) - np.asarray(densities_expected), 2))
    SS_tot_avg = SS_tot
    SS_res_avg = SS_res

    R_square = 1 - SS_res_avg / SS_tot_avg
    return R_square


def goodness_of_fit_summary(gmm_pdf_result, kde_result):
    error_array = np.power(gmm_pdf_result - kde_result, 2)

    MSE = np.average(error_array)
    RMSE = np.sqrt(MSE)
    R_square = R_square_of(MSE, kde_result)
    Chi_square = sum(error_array/gmm_pdf_result)

    gmm_cdf = cdf_from_pdf(gmm_pdf_result)
    kde_cdf = cdf_from_pdf(kde_result)
    diff = abs(gmm_cdf - kde_cdf)
    KS_stat = np.amax(diff)

    return {
        'MSE': MSE,
        'R_square': R_square,
        'Chi_square': Chi_square,
        'K_S': KS_stat,
        'RMSE / Max': RMSE/np.max(kde_result),
        'RMSE / Mean': RMSE/np.mean(kde_result),
    }


def cdf_from_pdf(pdf):
    if not isinstance(pdf[0], np.ndarray):
        original_dim = int(np.sqrt(len(pdf)))
        pdf = pdf.reshape(original_dim, original_dim)
    cdf = np.copy(pdf)
    xdim, ydim = cdf.shape
    for i in xrange(1, xdim):
        cdf[i,0] = cdf[i-1,0] + cdf[i,0]
    for i in xrange(1, ydim):
        cdf[0,i] = cdf[0,i-1] + cdf[0,i]
    for j in xrange(1, ydim):
        for i in xrange(1, xdim):
            cdf[i,j] = cdf[i-1,j] + cdf[i,j-1] - cdf[i-1,j-1] + pdf[i,j]
    return cdf


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
    if 'dat' in file_name:
        location_name = file_path.split('/')[-2]
    else:
        location_name = file_name.split('.txt')[0]
    return location_name


def generate_Z_from_X_Y(X,Y, Z_func):
    XX, YY=np.meshgrid(X,Y)
    coords=np.array((XX.ravel(), YY.ravel())).T
    Z = Z_func(coords).reshape(XX.shape)
    return Z
