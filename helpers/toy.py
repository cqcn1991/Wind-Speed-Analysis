# 1. Variability for cross validation determining bandiwdth
from sklearn.grid_search import GridSearchCV

# bandwidth_range = arange(0.7,2,0.1)
bandwidth_range = arange(0.7,2,0.2)

X = Y = PLOT_AXIS_RANGE

for i in arange(1,11):
    grid = GridSearchCV(neighbors.KernelDensity(kernel = KDE_KERNEL),
                        {'bandwidth': bandwidth_range},
                        n_jobs=-1, cv=4)

    df_resampled = df.sample(frac=1, replace=True)
    sample = array(zip(df_resampled.x, df_resampled.y))

    grid.fit(sample)
    bandwidth = grid.best_params_['bandwidth']
    print bandwidth, len(df_resampled)

    kde = neighbors.KernelDensity(bandwidth=bandwidth,kernel = KDE_KERNEL).fit(sample)

    kde_Z = generate_Z_from_X_Y(X,Y, lambda coords: exp(kde.score_samples(coords)))
    colorbar_lim = 0, kde_Z.max()

    fig,ax1 = plt.subplots(figsize=(4,3))
    plot_2d_prob_density(X,Y,kde_Z,xlabel='x', ylabel='y',ax=ax1)

    with sns.axes_style({'axes.grid' : False}):
        from matplotlib import ticker
        fig_hist,ax2 = plt.subplots(figsize=(4,3))
        _,_,_,image = ax2.hist2d(df_resampled.x, df_resampled.y, bins=PLOT_AXIS_RANGE, cmap='viridis',)
        ax2.set_aspect('equal')
        cb = plt.colorbar(image)
        plt_configure(ax=ax2, xlabel='x',ylabel='y')
    align_figures()

## 2. 4 fold Cross validation, comparison between train/test KDE
# %% time
from sklearn.cross_validation import train_test_split, KFold

## 5-fold cross validation
number_of_fold = 4

print bandwidth

kf = KFold(len(df), n_folds=number_of_fold, shuffle=True)
for train_index, test_index in kf:
    sub_df, sub_df_test = df.iloc[train_index], df.iloc[test_index]

    sample = array(zip(sub_df.x, sub_df.y))
    kde = neighbors.KernelDensity(bandwidth=bandwidth).fit(sample)

    X = Y = PLOT_AXIS_RANGE
    kde_Z = generate_Z_from_X_Y(X, Y, lambda coords: exp(kde.score_samples(coords)))
    fig, ax1 = plt.subplots(figsize=(4, 3))
    plot_2d_prob_density(X, Y, kde_Z, xlabel='x', ylabel='y', ax=ax1)

    sample = array(zip(sub_df_test.x, sub_df_test.y))
    kde_test = neighbors.KernelDensity(bandwidth=bandwidth).fit(sample)

    kde_Z = generate_Z_from_X_Y(X, Y, lambda coords: exp(kde_test.score_samples(coords)))
    fig, ax1 = plt.subplots(figsize=(4, 3))
    plot_2d_prob_density(X, Y, kde_Z, xlabel='x', ylabel='y', ax=ax1)
    align_figures()