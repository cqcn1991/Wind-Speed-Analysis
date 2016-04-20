from .shared_imports import *
from .utility_helper import chunks


def group_gmm_param_from_gmm_param_array(gmm_param_array, sort_group=True):
    from operator import itemgetter
    # from 17-1 -> 6-n array
    gmm = list(chunks(gmm_param_array, 6))
    if sort_group:
        gmm = sorted(gmm, key=itemgetter(0), reverse=True)  # reorder by fraction, from big to small
    return gmm


# GMM result
def read_gmm_em_result(clf):
    gmm_em_result = []
    for i in xrange(clf.n_components):
        weight = clf.weights_[i]
        meanx, meany = clf.means_[i].tolist()
        sigx, sigy = np.sqrt(clf.covars_[i][0, 0]), np.sqrt(clf.covars_[i][1, 1])
        rho = clf.covars_[i][0, 1]/(sigx*sigy)
        gaussian_params = weight, meanx, meany, sigx, sigy, rho
        gmm_em_result.extend(gaussian_params)
    return gmm_em_result


def create_gaussian_2d(meanx, meany, sigx, sigy, rho):
    from scipy.stats import multivariate_normal
    sigxy = rho*sigx*sigy
    return multivariate_normal(mean=[meanx, meany],
                               cov=[[sigx**2, sigxy], [sigxy, sigy**2]],
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
    a = np.sqrt(w[0])
    b = np.sqrt(w[1])
    return a/b


def width_height_ratios_set(gmm):
    gmm = group_gmm_param_from_gmm_param_array(gmm, sort_group=False)
    ratios_set = [width_height_ratio(g) for g in gmm]
    return np.asarray(ratios_set)