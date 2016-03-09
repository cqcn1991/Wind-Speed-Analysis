from .shared_imports import *

def R_square_of(MSE, kde_result):
    # R square measure:
    # https://en.wikipedia.org/wiki/Coefficient_of_determination
    # Measures Model-Observation variance against Observation-Average variacen
    y_mean = np.mean(kde_result)
    SS_tot = np.power(kde_result - y_mean,2)
    SS_tot_avg = np.average(SS_tot)

    SS_res_avg = MSE
    R_square = 1 - SS_res_avg/SS_tot_avg

    return R_square


def goodness_of_fit_summary(gmm_pdf_result, kde_result, count):
    error_array = np.power(gmm_pdf_result - kde_result,2)

    MSE = np.average(error_array)
    RMSE = np.sqrt(MSE)
    R_square = R_square_of(MSE, kde_result)
    # Chi_square = sum(error_array/gmm_pdf_result) * count
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
        pdf = pdf.reshape(original_dim,original_dim)
    cdf = np.copy(pdf)
    xdim, ydim = cdf.shape
    for i in xrange(1,xdim):
         cdf[i,0] =  cdf[i-1,0] +  cdf[i,0]
    for i in xrange(1,ydim):
         cdf[0,i] =  cdf[0,i-1] +  cdf[0,i]
    for j in xrange(1,ydim):
        for i in xrange(1,xdim):
             cdf[i,j] =  cdf[i-1,j] +  cdf[i,j-1] -  cdf[i-1,j-1] + pdf[i,j]
    return cdf

def pretty_print_gmm(gmm):
    from gmm_helper import group_gmm_param_from_gmm_param_array
    if not isinstance(gmm[0], np.ndarray):
        gmm = group_gmm_param_from_gmm_param_array(gmm, sort_group = True)
    pretty_result = pd.DataFrame(gmm, columns = ['weight','mean_x','mean_y','sig_x','sig_y','corr'])
    return pretty_result