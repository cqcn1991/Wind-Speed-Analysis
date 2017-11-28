from .shared_imports import *


def bivar_empirical_limit(df_all_years, config):
    from .plot_print_helper import plt_configure
    from .app_helper import fit_kde
    from .parallel_helper import kde_gofs
    fig1, ax1 = plt.subplots(figsize=(3, 2.5))
    fig2, ax2 = plt.subplots(figsize=(3, 2.5))
    gofs_mean_set_bivar, gofs_bivar_set = [], {}

    # for year_length, line_style in zip([5, 7, 10], ['-.','--', '-']):
    for year_length, line_style in zip([5, 10], ['-.', '-']):
        # 1. Set time
        start_year, end_year = df_all_years.index.year[0], 2015 - year_length + 1
        # 2. Obtain gofs_bivar
        df_standard = df_all_years[str(2015 - year_length + 1):'2015']
        kde_result_standard, _ = fit_kde(df_standard, config)
        gofs_bivar = Parallel(n_jobs=-1)(
            delayed(kde_gofs)(df_all_years[str(start_year):str(start_year + year_length - 1)], kde_result_standard,
                              config)
            for start_year in arange(start_year, end_year + 1))
        gofs_bivar_set[year_length] = gofs_bivar = pd.DataFrame(gofs_bivar, index=arange(start_year, end_year + 1))

        if len(gofs_bivar) > 0:
            # 3. Make plot
            gofs_bivar.plot(y='R_square', ax=ax1, label=str(year_length) + ' years', style=line_style)
            gofs_bivar.plot(y='K_S', ax=ax2, label=str(year_length) + ' years', style=line_style)
            # 4. Obtain gofs averaged over late 5 years
            year_lim = end_year - year_length - 5, end_year - year_length
            gofs_mean = gofs_bivar.query('index >= @year_lim[0] & index <= @year_lim[1]').mean().to_dict()
            gofs_mean['year_lim'] = year_lim
            gofs_mean_set_bivar.append(gofs_mean)

    if len(gofs_mean_set_bivar) > 0:
        gofs_mean_set_bivar = pd.DataFrame(gofs_mean_set_bivar).set_index('year_lim')
    plt_configure(ax=ax1, ylabel='$\ R^2$', xlabel='Start year')
    plt_configure(ax=ax2, ylabel='K-S', xlabel='Start year')
    return gofs_bivar_set, gofs_mean_set_bivar, fig1, fig2


def kde_univar_gof(df_standard, df, x):
    from .app_helper import empirical_marginal_distribution, sector_r_square
    _, _, density, y_ecdf, density_dir = empirical_marginal_distribution(df_standard, x)
    _, _, density_expected, y_ecdf_previous, density_dir_expected = empirical_marginal_distribution(df, x)

    # 1. Speed
    r_square = sector_r_square(density, density_expected)
    k_s = max(np.abs(y_ecdf - y_ecdf_previous))

    # 2. Direction
    r_square_dir = sector_r_square(density_dir, density_dir_expected)
    return {'r_square': r_square, 'k_s': k_s, 'r_square_dir': r_square_dir}


def univar_empirical_limit(df, df_all_years):
    from .plot_print_helper import plt_configure
    x = arange(0, df.speed.max() + 1)
    fig1, ax1 = plt.subplots(figsize=(2.7,2.4))
    fig2, ax2 = plt.subplots(figsize=(2.7,2.4))
    fig3, ax3 = plt.subplots(figsize=(2.7,2.4))
    gofs_mean_set, gofs_univar_set = [], {}

    for year_length, line_style in zip([5, 7, 10], ['-.', '--','-']):
        # 1. Set time
        start_year, end_year =df_all_years.index.year[0], 2015-year_length+1
        # 2. Obtain gofs
        df_standard = df_all_years[str(2015-year_length+1):str(2015)]
        gofs = [kde_univar_gof(df_standard, df_all_years[str(start_year):str(start_year+year_length-1)], x)
                for start_year in arange(start_year, end_year+1)]
        # 3. Make plot
        if len(gofs)>0:
            gofs_univar_set[year_length]=gofs = pd.DataFrame(gofs, index=arange(start_year, end_year+1))
            ax1.plot(gofs.r_square, line_style, label=str(year_length)+' years')
            ax2.plot(gofs.k_s, line_style, label=str(year_length)+' years')
            ax3.plot(gofs.r_square_dir, line_style, label=str(year_length)+' years')
        # 4. Obtain gofs averaged over late 5 years
            year_lim = end_year-year_length-5, end_year-year_length
            gofs_mean = gofs.query('index >= @year_lim[0] & index <= @year_lim[1]').mean().to_dict()
            gofs_mean['year_lim']=year_lim
            gofs_mean_set.append(gofs_mean)
    for ax, ylabel in zip([ax1, ax2, ax3], ['$\ R^2$','K-S', '$\ R^2$']):
        plt_configure(ax=ax, xlabel='Start year', ylabel=ylabel, tight='xtight', legend=True)
    if len(gofs_mean_set)>0:
        gofs_mean_set = pd.DataFrame(gofs_mean_set).set_index('year_lim')
    return gofs_univar_set, gofs_mean_set, fig1, fig2, fig3