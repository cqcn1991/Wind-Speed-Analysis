from .shared_imports import *
from .gmm_helper import group_gmm_param_from_gmm_param_array


def plot_gmm_ellipses(gmm, ax=None):
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
                                  angle=angle, alpha=0.7, color=next(prop_cycle))
        ax.add_patch(ell)

    ax.autoscale()
    ax.set_aspect('equal')
    plt.show()


def plot_speed_and_angle_distribution(df_speed, df_dir, title=None):
    prop_cycle = iter(sns.color_palette())
    plt.subplot(1, 2, 1)
    bins = np.arange(0, 40 + 1, 1)
    df_speed.hist(bins=bins, color=next(prop_cycle))
    plt.xlabel("Speed")

    plt.subplot(1, 2, 2)
    bins = np.arange(-5, 360, 10)
    df_dir.hist(bins=bins, figsize=(15, 3), color=next(prop_cycle))
    plt.xlabel("Direction")
    plt.axis('tight')
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
    return pretty_result



