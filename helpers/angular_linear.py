from .shared_imports import *


def div0( a, b ):
    """ ignore / 0, div0( [-1, 0, 1], 0 ) -> [0, 0, 0] """
    with np.errstate(divide='ignore', invalid='ignore'):
        c = np.true_divide( a, b )
        c[ ~ np.isfinite( c )] = 0  # -inf inf NaN
    return c


def angular_linear_pdf(x, alpha, speed_params, vonmises_params, connection_params, cartesian=False):
    from scipy.stats import kappa4, vonmises
    from numpy import inf
    # 1. Speed
    k, h, scale, loc = speed_params
    x_pdf = kappa4.pdf(x, h, k, loc=loc, scale=scale)
    x_cdf = kappa4.cdf(x, h, k, loc=loc, scale=scale)
    # 2. Direction
    alpha_pdf, alpha_cdf = 0, 0
    for k, u, w in vonmises_params:
        alpha_pdf = alpha_pdf + vonmises.pdf(alpha, k, loc=u, scale=1)*w
        alpha_cdf = alpha_cdf + vonmises.cdf(alpha, k, loc=u, scale=1)*w
    # 3. Connection
    phi = 2*pi*(x_cdf-alpha_cdf)
    phi_pdf_ = [vonmises.pdf(phi, k, loc=u, scale=1)*w for k, u, w in connection_params]
    phi_pdf = 0
    for i in range(len(connection_params)):
        phi_pdf = phi_pdf + phi_pdf_[i]
    if cartesian == True:
        pdf = div0(2*pi*x_pdf*alpha_pdf*phi_pdf, x)
    else:
        pdf = 2*pi*x_pdf*alpha_pdf*phi_pdf
    return pdf


def phi_from_speed_dir(df_speed, df_dir, speed_params, dir_params):
    from scipy.stats import kappa4, vonmises
    k, h, scale, loc = speed_params
    speed_cdf = kappa4.cdf(df_speed, h, k, loc=loc, scale=scale)
    alpha_cdf = 0
    for k, u, w in dir_params:
        alpha_cdf = alpha_cdf + vonmises.cdf(df_dir / 180 * pi, k, loc=u) * w
    phi = 2 * pi * (speed_cdf - alpha_cdf) % (2 * pi)
    return phi


def von_mises_mixture_pdf(x, vonmises_params):
    from scipy.stats import vonmises
    y = 0
    for k, u, w in vonmises_params:
        y = y + vonmises.pdf(x, k, loc=u) * w
    return y