from .shared_imports import *
from .gmm_helper import group_gmm_param_from_gmm_param_array


def pdf_comparison(X, Y, kde_Z, pdf_Z):
    fig = plt.figure(figsize=(6, 3))
    with sns.axes_style({'axes.grid': False}):
        ax1 = fig.add_subplot(1, 2, 1)
        plot_2d_prob_density(X, Y, kde_Z, colorbar=False)
        ax2 = fig.add_subplot(1, 2, 2)
        plot_2d_prob_density(X, Y, pdf_Z, colorbar=False)


def plt_configure(ax=None, xlabel=None, ylabel=None, title='', legend=False, tight=False, figsize=False, no_axis=False):
    if ax == None :
        ax=plt.gca()
        plt.suptitle(title)
    else:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if legend:
        if isinstance(legend, dict):
            ax.legend(**legend)
        else:
            ax.legend()
    if tight:
        if tight == 'xtight' or tight == 'x':
            ax.autoscale(enable=True, axis='x', tight=True)
        elif tight == 'ytight':
            ax.autoscale(enable=True, axis='y', tight=True)
        else:
            ax.axis('tight')
    if figsize:
        plt.gcf().set_size_inches(figsize)
    if no_axis:
        plt.gca().axis('off')
        legend = ax.legend()
        if legend:
            legend.remove()


def pretty_pd_display(data):
    return display(pd.DataFrame(data))


def plot_3d_prob_density(X, Y, Z, ax=None):
    if ax is None:
        fig = plt.figure()
        ax = plt.gca(projection='3d')
    X, Y = np.meshgrid(X, Y)
    surf = ax.plot_surface(
        X, Y, Z,rstride=1, cstride=1, cmap='viridis',
        linewidth=0, antialiased=False)
    plt.gca().set_aspect('equal')


def plot_2d_prob_density(X, Y, Z, xlabel = '', ylabel = '', ax=None, colorbar_lim=None, colorbar=True):
    from matplotlib import ticker
    # contourf accept vmin, vmax
    if ax is None:
        ax = plt.gca()
    CS = ax.contourf(X, Y, Z, 8, alpha=.75, cmap='viridis')
    ax.set_aspect('equal')
    plt_configure(ax=ax,xlabel=xlabel, ylabel=ylabel)
    if colorbar:
        cb = plt.colorbar(CS)
        tick_locator = ticker.MaxNLocator(nbins=6)
        cb.locator = tick_locator
        cb.update_ticks()


def plot_gmm_ellipses(gmm, ax=None, xlabel='x', ylabel='y'):
    from operator import itemgetter
    if 'sns' in globals():
        prop_cycle = iter(sns.color_palette("hls", 6))
    else:
        prop_cycle = iter(mpl.rcParams['axes.color_cycle'])
    if ax is None:
        fig, ax = plt.subplots(figsize=(3.5, 3.5))
    print('GMM Plot Result')
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
                                  angle=angle, alpha=0.7, color=next(prop_cycle), label="{0:.3f}".format(g[0]))
        ax.add_patch(ell)

    ax.autoscale()
    ax.set_aspect('equal')
    plt_configure(xlabel='x', ylabel='y',legend={'loc':'best'})
    # plt.show()


def plot_speed_and_angle_distribution(df_speed, df_dir, title='', speed_limit=None):
    if speed_limit == None:
        speed_limit = df_speed.max()
    prop_cycle = iter(mpl.rcParams['axes.color_cycle'])
    plt.subplot(1, 2, 1)
    bins = np.arange(0, speed_limit + 1, 1)
    df_speed.hist(bins=bins, color=next(prop_cycle))
    plt.locator_params(axis='y', nbins=5)
    plt_configure(xlabel="Speed", ylabel="Frequency", tight='y')

    plt.subplot(1, 2, 2)
    bins = np.arange(-5, df_dir.max()+10, 10)
    df_dir.hist(bins=bins, color=next(prop_cycle))
    plt_configure(xlabel="Direction", ylabel="Frequency", tight='xtight')
    plt.gcf().set_size_inches(10, 1.2)
    plt.locator_params(axis='y', nbins=5)
    if title:
        plt.suptitle(title, y=1.08)
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


def gof_df(gmm_pdf_result, kde_result):
    from app_helper import goodness_of_fit_summary
    gof_df = pd.DataFrame([goodness_of_fit_summary(gmm_pdf_result, kde_result)])
    gof_df = gof_df[['R_square', 'K_S','Chi_square', 'MSE', 'RMSE / Max', 'RMSE / Mean']]
    return gof_df.applymap(lambda x: "{0:.3f}".format(x) if x > 0.005 else x)


def check_time_shift(df):
    from app_helper import myround
    speed_limit = df.speed.max()
    init_time = myround(df.date.min() // 10000, 5) * 10000
    for start_time in xrange(init_time, 20160000, 50000):
        end_time = min(start_time + 50000, df.date.max()+ 10000)
        sub_df = df.query('(date >= @start_time) & (date < @end_time)')
        if len(sub_df) > 0 :
            title = '%s - %s' %(sub_df.date.min()//10000, sub_df.date.max()//10000)
            print title
            plot_speed_and_angle_distribution(sub_df.speed, sub_df.dir, speed_limit=speed_limit)



