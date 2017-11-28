from .shared_imports import *
from lmoments3 import distr

def div0( a, b ):
    """ ignore / 0, div0( [-1, 0, 1], 0 ) -> [0, 0, 0] """
    with np.errstate(divide='ignore', invalid='ignore'):
        c = np.true_divide(a, b)
        c[~ np.isfinite(c)] = 0  # -inf inf NaN
    return c


def angular_linear_pdf(x, alpha, kap_params, vonmises_params, connection_params, cartesian=False):
    from scipy.stats import kappa4, vonmises
    # 1. Speed
    k, h, scale, loc = kap_params['k'], kap_params['h'], kap_params['scale'], kap_params['loc']
    x_pdf = kappa4.pdf(x, h, k, loc=loc, scale=scale)
    x_cdf = kappa4.cdf(x, h, k, loc=loc, scale=scale)
    # 2. Direction
    alpha_pdf = np.sum([vonmises.pdf(alpha, k, loc=u) * w for k, u, w in vonmises_params], axis=0)
    alpha_cdf = np.sum([vonmises.cdf(alpha, k, loc=u) * w for k, u, w in vonmises_params], axis=0)
    # 3. Connection
    phi = 2*pi*(x_cdf-alpha_cdf)
    phi_pdf = np.sum([vonmises.pdf(phi, k, loc=u) * w for k, u, w in connection_params], axis=0)
    if cartesian == True:
        pdf = div0(2*pi*x_pdf*alpha_pdf*phi_pdf, x)
    else:
        pdf = 2*pi*x_pdf*alpha_pdf*phi_pdf
    return pdf


def generate_al_pdf_from(kap_params, vonmises_params, connection_params, cartesian=False):
    def al_pdf(x, alpha):
        return angular_linear_pdf(x, alpha, kap_params, vonmises_params, connection_params, cartesian=cartesian)
    return al_pdf


def phi_from_speed_dir(df_speed, df_dir, kap_params, dir_params):
    from scipy.stats import kappa4, vonmises
    k, h, scale, loc = kap_params['k'], kap_params['h'], kap_params['scale'], kap_params['loc']
    speed_cdf = kappa4.cdf(df_speed, h, k, loc=loc, scale=scale)
    alpha_cdf = np.sum([vonmises.cdf(df_dir/180*pi, k, loc=u) * w for k, u, w in dir_params], axis=0)
    phi = 2*pi*(speed_cdf - alpha_cdf)%(2*pi)
    return phi


def von_mises_mixture_pdf(x, vonmises_params):
    from scipy.stats import vonmises
    y = np.sum([vonmises.pdf(x, k, loc=u) * w for k, u, w in vonmises_params], axis=0)
    return y


def al_integration_in_direction(f, start_radian, end_radian, bins, bin_width):
    from scipy import integrate
    direction_prob = integrate.nquad(f, [[0, inf], [start_radian, end_radian]])[0]
    density_expected_ = array([sp.integrate.nquad(f, [[x_, x_+bin_width], [start_radian, end_radian]])
        for x_ in bins[:-1]])[:, 0]
    density_expected = density_expected_/direction_prob/bin_width
    y_cdf = np.append(0, np.cumsum(density_expected)*bin_width)
    # y_cdf = array([integrate.nquad(f, [[0, x_val], [start_radian, end_radian]])
    #                for x_val in bins])[:, 0]/direction_prob
    # y_cdf = None
    return bins, density_expected, y_cdf, direction_prob


def al_univar_gof(df_standard, kap_params, dir_params, x, bin_width):
    from .app_helper import empirical_marginal_distribution, sector_r_square
    _, _, density, y_ecdf, density_dir = empirical_marginal_distribution(df_standard, x)
    bins = x
    kap = distr.kap(**kap_params)
    density_expected_kap = kap.cdf(bins[1:]) - kap.cdf(bins[:-1])
    y_cdf_kappa = kap.cdf(x)

    theta = linspace(0, 2 * pi, num=36 + 1)
    y_vonmises = von_mises_mixture_pdf(theta, dir_params)

    r_square = sector_r_square(density * bin_width, density_expected_kap)
    k_s = max(np.abs(y_cdf_kappa - y_ecdf))
    r_square_dir = sector_r_square(density_dir * 10, (y_vonmises * 2 * pi / 36)[:-1])

    return {'r_square': r_square, 'k_s': k_s, 'r_square_dir': r_square_dir}

def original_cabo_degata_params():
    speed_params = k, h, scale, loc = 0.351, 0.626, 5.095, 2.508
    vonmises_params = [
        [1.101, 1.430, 0.115],
        [16.989, 1.155, 0.239],
        [14.661, 4.446, 0.301],
        [2.793, 0.733, 0.172],
        [2.512, 4.282, 0.173]]
    connection_params = [
        [0.746, 0.774, 0.486],
        [0.883, 4.073, 0.514]]

    al_params = [speed_params, vonmises_params, connection_params]
    return al_params