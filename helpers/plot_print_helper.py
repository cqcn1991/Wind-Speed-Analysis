from .shared_imports import *
from .gmm_helper import group_gmm_param_from_gmm_param_array


def plt_configure(xlabel='', ylabel='', title=None, legend=False, tight=False):
    if title:
        plt.suptitle(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if legend:
        if isinstance(legend, dict):
            plt.legend(**legend)
        else:
            plt.legend()
    if tight:
        if tight == 'xtight':
            plt.autoscale(enable=True, axis='x', tight=True)
        elif tight == 'ytight':
            plt.autoscale(enable=True, axis='y', tight=True)
        else:
            plt.axis('tight')


def pretty_pd_display(data):
    return display(pd.DataFrame(data))


def plot_3d_prob_density(X, Y, Z, ax=None):
    if ax is None:
        fig = plt.figure()
        # fig.set_size_inches(14, 6)
        ax = fig.gca(projection='3d')
    ax.set_aspect('equal')
    X, Y = np.meshgrid(X, Y)
    surf = ax.plot_surface(
        X, Y, Z,rstride=1, cstride=1, cmap='jet',
        linewidth=0, antialiased=False)


def plot_2d_prob_density(X, Y, Z, ax=None, xlabel = '', ylabel = ''):
    # For docs, see `help(plt.contour)`
    if ax is None:
        fig, ax = plt.subplots()
    ax.set_aspect('equal')
    CS = plt.contourf(X, Y, Z, 10, alpha=.75, cmap='jet')
    plt_configure(xlabel, ylabel)
    plt.colorbar(CS)


def plot_gmm_ellipses(gmm, ax=None, xlabel='x', ylabel='y'):
    from operator import itemgetter
    prop_cycle = iter(sns.color_palette("hls", 6))
    if ax is None:
        fig, ax = plt.subplots()
    print 'GMM Plot Result'
    if not isinstance(gmm[0], np.ndarray) and not isinstance(gmm[0], list):
        gmm = group_gmm_param_from_gmm_param_array(gmm, sort_group=False)
    gmm = sorted(gmm, key=itemgetter(0),reverse=True)
    for i, g in enumerate(gmm):
        xy_mean = np.matrix([g[1], g[2]])
        sigx, sigy, sigxy = g[3], g[4], g[5]*g[3]*g[4]
        cov_matrix = np.matrix([[sigx**2, sigxy], [sigxy, sigy**2]])

        # eigenvalues, and eigen vector
        w, v = np.linalg.eigh(cov_matrix)

        # normalized the eigen vector
        uu = v[0] / np.linalg.norm(v[0])
        # rotation angle, from x, y to u, v
        angle_arc = np.arctan2(uu[0, 1], uu[0, 0])
        angle = np.degrees(angle_arc)

        transform_matrix = np.matrix([[np.cos(angle_arc), -np.sin(angle_arc)],
                                      [np.sin(angle_arc), np.cos(angle_arc)]])
        xy_mean_in_uv = transform_matrix * xy_mean.T

        # print fraction, rotation agnle, u v mean(in standalone panel), std
        print g[0], xy_mean, np.sqrt(w), angle

        ell = mpl.patches.Ellipse(xy=xy_mean.T, width=2*np.sqrt(w[0]), height=2*np.sqrt(w[1]),
                                  angle=angle, alpha=0.7, color=next(prop_cycle), label = "{0:.3f}".format(g[0]))
        ax.add_patch(ell)

    ax.autoscale()
    ax.set_aspect('equal')
    plt_configure(legend=True)
    plt.show()


def plot_speed_and_angle_distribution(df_speed, df_dir, title=''):
    prop_cycle = iter(sns.color_palette())
    plt.subplot(1, 2, 1)
    bins = np.arange(0, 40 + 1, 1)
    df_speed.hist(bins=bins, color=next(prop_cycle))
    plt_configure("Speed", "Frequency")

    plt.subplot(1, 2, 2)
    bins = np.arange(-5, 360, 10)
    df_dir.hist(bins=bins, figsize=(15, 3), color=next(prop_cycle))
    plt_configure(xlabel="Direction", ylabel="Frequency", tight='xtight')
    if title:
        plt.suptitle(title)
    plt.show()


def pretty_print_gmm(gmm):
    from gmm_helper import group_gmm_param_from_gmm_param_array
    if not isinstance(gmm[0], np.ndarray) and not isinstance(gmm[0], list):
        gmm = group_gmm_param_from_gmm_param_array(gmm, sort_group=True)
    pretty_result = pd.DataFrame(gmm, columns=['weight',
                                               'mean_x', 'mean_y',
                                               'sig_x', 'sig_y','corr'])
    pretty_result.index += 1
    decimal_format = lambda x: "{0:.3f}".format(x)
    return pretty_result.applymap(decimal_format)



