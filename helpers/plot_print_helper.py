from .shared_imports import *


def pdf_comparison(X, Y, kde_Z, pdf_Z):
    fig = plt.figure(figsize=(6, 3))
    with sns.axes_style({'axes.grid': False}):
        ax1 = fig.add_subplot(1, 2, 1)
        plot_2d_prob_density(X, Y, kde_Z, colorbar=False)
        ax2 = fig.add_subplot(1, 2, 2)
        plot_2d_prob_density(X, Y, pdf_Z, colorbar=False)


def plt_configure(ax=None, xlabel=None, ylabel=None, title='', legend=False, tight=False, figsize=False, no_axis=False, xunit_text=None):
    if ax == None :
        ax=plt.gca()
        plt.suptitle(title)
    else:
        ax.set_title(title)
    if xlabel:
        if xunit_text:
            xlabel=xlabel+xunit_text
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


def plot_2d_prob_density(X, Y, Z, xlabel='', ylabel='', ax=None, colorbar_lim=None, colorbar=True):
    from matplotlib import ticker
    # contourf accept vmin, vmax
    if ax is None:
        ax = plt.gca()
    CS = ax.contourf(X, Y, Z, 10, alpha=.75, cmap='viridis')
    ax.set_aspect('equal')
    plt_configure(ax=ax, xlabel=xlabel, ylabel=ylabel)
    if colorbar:
        cb = plt.colorbar(CS)
        tick_locator = ticker.MaxNLocator(nbins=6)
        cb.locator = tick_locator
        cb.update_ticks()


def plot_gmm_ellipses(gmm, ax=None, xlabel='x', ylabel='y', unit_text=' (knot)'):
    from operator import itemgetter
    from .gmm_helper import group_gmm_param_from_gmm_param_array
    if ax is None:
        fig, ax = plt.subplots(figsize=(3.5, 3.5))
    # print('GMM Plot Result')
    if not isinstance(gmm[0], np.ndarray) and not isinstance(gmm[0], list):
        gmm = group_gmm_param_from_gmm_param_array(gmm, sort_group=False)
    gmm = sorted(gmm, key=itemgetter(0),reverse=True)
    if 'sns' in globals():
        prop_cycle = iter(sns.color_palette("hls", len(gmm)))
    else:
        prop_cycle = iter(mpl.rcParams['axes.color_cycle'])
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
        # print(g[0], xy_mean, np.sqrt(w), angle)

        color = next(prop_cycle)
        ell = mpl.patches.Ellipse(xy=xy_mean.T, width=2*np.sqrt(w[0]), height=2*np.sqrt(w[1]),
                                  angle=angle, alpha=0.7, color=color, label="{0:.3f}".format(g[0]))
        ax.add_patch(ell)
        x_mean, y_mean = xy_mean.tolist()[0]
        ax.plot(x_mean,y_mean, 'o',color=color)
        axis_1_x,axis_1_y = np.sqrt(w[0])*np.cos(angle_arc), np.sqrt(w[0])*np.sin(angle_arc)
        ax.plot([x_mean-axis_1_x, x_mean+axis_1_x],[y_mean-axis_1_y, y_mean+axis_1_y],'-',color=color)
        axis_2_x,axis_2_y = -np.sqrt(w[1])*np.sin(angle_arc), np.sqrt(w[1])*np.cos(angle_arc)
        ax.plot([x_mean-axis_2_x, x_mean+axis_2_x],[y_mean-axis_2_y, y_mean+axis_2_y],'-',color=color)

    ax.autoscale()
    ax.set_aspect('equal')
    plt_configure(xlabel=xlabel, ylabel=ylabel, legend={'loc':'best'})


def plot_speed_and_angle_distribution(df_speed, df_dir, title='', speed_limit=None, speed_unit_text='', dir_unit_text='', bin_width=1):
    if speed_limit is None:
        speed_limit = df_speed.max()
    prop_cycle = iter(mpl.rcParams['axes.color_cycle'])
    plt.subplot(1, 2, 1)
    bins = np.arange(0, speed_limit + bin_width, bin_width)
    df_speed.hist(bins=bins, color=next(prop_cycle))
    plt.locator_params(axis='y', nbins=5)
    plt_configure(xlabel="Speed"+speed_unit_text, ylabel="Frequency", tight='y')

    plt.subplot(1, 2, 2)
    bins = np.arange(-5, df_dir.max()+10, 10)
    df_dir.hist(bins=bins, color=next(prop_cycle))
    plt_configure(xlabel="Direction"+dir_unit_text, ylabel="Frequency", tight='xtight')
    plt.gcf().set_size_inches(7, 1.7)
    plt.tight_layout()
    plt.locator_params(axis='y', nbins=5)
    if title:
        plt.suptitle(title, y=1.08)
    plt.show()


def check_time_shift(df, speed_unit_text='', dir_unit_text='', bin_width=1):
    from .app_helper import myround
    speed_limit = min(40, df.speed.max())
    init_time = (myround(df.date.min() // 10000, 5)+1) * 10000
    for start_time in range(init_time, 20200000, 50000):
        end_time = min(start_time + 50000, df.date.max() + 10000)
        sub_df = df.query('(date >= @start_time) & (date < @end_time)')
        if len(sub_df) > 0:
            title = '%s - %s' % (sub_df.date.min() // 10000, sub_df.date.max() // 10000)
            print(title)
            plot_speed_and_angle_distribution(sub_df.speed, sub_df.dir, speed_limit=speed_limit,
                                              speed_unit_text=speed_unit_text, dir_unit_text=dir_unit_text, bin_width=bin_width)


def pretty_print_gmm(gmm):
    from .gmm_helper import group_gmm_param_from_gmm_param_array
    if not isinstance(gmm[0], np.ndarray) and not isinstance(gmm[0], list):
        gmm = group_gmm_param_from_gmm_param_array(gmm, sort_group=True)
    pretty_result = pd.DataFrame(gmm, columns=['weight',
                                               'mean_x', 'mean_y',
                                               'sig_x', 'sig_y','corr'])
    pretty_result.index += 1
    decimal_format = lambda x: "{0:.3f}".format(x)
    return pretty_result.applymap(decimal_format)


def gof_df(gmm_pdf_result, kde_result, bin_width=1):
    from .app_helper import goodness_of_fit_summary
    gof_df = pd.DataFrame([goodness_of_fit_summary(gmm_pdf_result, kde_result, bin_width=bin_width)])
    gof_df = gof_df[['R_square', 'K_S','Chi_square', 'Chi_square_2', 'MSE', 'RMSE / Max', 'RMSE / Mean']]
    return gof_df.applymap(lambda x: "{0:.3f}".format(x) if x > 0.005 else x)


def nominal_avg_and_weight_avg(df_weight, df_value):
    return np.average(df_value), np.sum(df_weight/df_weight.sum() * df_value)


def plot_sectoral_comparison(vals, direction, datasize):
    means = []
    line_styles = ['-', '--', '-.']
    for v, line_style in zip(vals, line_styles):
        # Weighted average by datasize at each direction
        _, mean = nominal_avg_and_weight_avg(datasize, v['value'])
        line, = plt.plot(direction, v['value'], line_style, label=v['name'], marker='o')
        plt.axhline(mean, linestyle=line_style, color=line.get_color(), label=v['name'] + ' weighted average')
        means.append(mean)

    plt_configure(xlabel='Direction (degree)', legend={'loc': 'best'}, figsize=(4, 2.5))
    plt.locator_params(axis='y', nbins=5)
    return means
