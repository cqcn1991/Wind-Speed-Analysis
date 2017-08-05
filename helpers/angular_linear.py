from .shared_imports import *


def angular_linear_pdf(x, alpha, speed_params, vonmises_params, connection_params):
    from scipy.stats import kappa4, vonmises
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
    return 2*pi*x_pdf*alpha_pdf*phi_pdf

