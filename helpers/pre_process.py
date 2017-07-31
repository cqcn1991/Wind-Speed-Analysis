from .shared_imports import *
from .plot_print_helper import plt_configure


def is_with_too_many_zero(df, threshold=1.5):
    too_many_zero = False
    bins = arange(0, df.speed.max())
    count, _ = np.histogram(df['speed'], bins=bins)
    null_wind_frequency = count[0]/len(df)
    if null_wind_frequency >= 0.1:
        too_many_zero = True
    return too_many_zero, null_wind_frequency


def realign_direction(df, effective_column):
    if len(effective_column) == 16:
        # For some dataset, the angle is not evenly distributed, so there is a need to redistribute
        original_angle = list(effective_column.sort_index().index)
        redistributed_angle = linspace(0, 360, num=17)[:-1]
        df['dir'].replace(to_replace=original_angle, value=redistributed_angle, inplace=True)
        display(df['dir'].value_counts().sort_index())
    return df


def fill_direction_999(df, SECTOR_LENGTH, integer_data):
    # df = df.copy()
    fig = plt.figure()
    df['wind_type'].value_counts().plot(
        kind='bar', title='Wind Types Comprisement', figsize=(4, 3))

    if len(df.query('dir == 999')) >= 1:
        fig = plt.figure()
        bins = arange(0, df.dir.max() + 100, 10)
        df['dir'].plot(kind='hist', alpha=0.5, bins=bins, label='before interpolation')
        df['dir'] = df.apply(lambda x: np.nan if x.dir == 999 else x.dir, axis=1)
        # Force to integer direction interval
        if integer_data:
            df['dir'] = df['dir'].interpolate() // SECTOR_LENGTH * SECTOR_LENGTH
        else:
            df['dir'] = df['dir'].interpolate()
        df['dir'].plot(kind='hist', alpha=0.5, bins=bins, label='after interpolation')
        plt_configure(title='Dir 999 record handling comparison', figsize=(8, 3), legend={'loc': 'best'})
    return df


def randomize_angle(df, DIR_REDISTRIBUTE, sector_span = 10):
    df = df.copy()
    if DIR_REDISTRIBUTE == 'even':
        df['dir_ran'] = df['dir'].apply(lambda x: (x + np.random.uniform(-sector_span/2,sector_span/2)))
    else:
        df['dir_ran'] = df['dir'].apply(lambda x: (x + np.random.uniform(0,sector_span)))

    bins=arange(0, 360+10, 5)
    df['dir'].hist(bins=bins, alpha=0.5, label='Original Data')
    bins=arange(0, 360+10, 1)
    df['dir_ran'].hist(bins=bins, alpha=0.5, label='Redistributed Data')
    plt_configure(xlabel="Direction", ylabel="Frequency", tight='x',
                  legend={'loc':'best'}, figsize=(8, 3))

    df['dir']=df['dir_ran']
    df.drop(['dir_ran'], 1,inplace=True)
    return df


def randomize_speed(df, redistribute_method='up'):
    df = df.copy()
    # Round down speed, need more caution
    if redistribute_method == 'up':
        speed_redistribution_info = 'Redistribute upward, e.g. 0 -> [0,1]'
        df['speed_ran'] = df['speed'].apply(lambda x: (x + np.random.uniform(0,1)))
    elif redistribute_method == 'down':
        speed_redistribution_info = 'Redistribute downward, e.g. 1 -> [0,1]'
        df['speed_ran'] = df['speed'].apply(lambda x: (x + np.random.uniform(-1,0)) if x > 0 else x)
    elif redistribute_method == 'even':
        speed_redistribution_info = 'Redistribute evenly, e.g. 0 -> [0, 0.5]; 1 -> [0.5,1.5]'
        df['speed_ran'] = df['speed'].apply(lambda x: (x + np.random.uniform(-0.5,0.5)) if x > 0 else x+ np.random.uniform(0, 0.5))

    max_speed = df.speed.max()
    df['speed'].hist(bins=arange(0, max_speed), alpha=0.5, label='Original Data')
    df['speed_ran'].hist(bins=arange(0, max_speed, 0.5), alpha=0.5, label='Redistributed Data')
    print(speed_redistribution_info)
    plt_configure(xlabel="Speed", ylabel="Frequency", legend=True, figsize=(8, 3))

    df['speed']=df['speed_ran']
    df.drop(['speed_ran'], 1, inplace=True)
    return df, speed_redistribution_info
