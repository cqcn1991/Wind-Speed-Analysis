from __future__ import division
from .shared_imports import *
from plot_print_helper import plt_configure

def is_with_too_many_zero(df, threshold=1.5):
    too_many_zero = False
    bins = arange(0, df.speed.max())
    count, _ = np.histogram(df['speed'], bins=bins)
    null_wind_frequency = count[0]/len(df)
    if count[0]/count[1] >= threshold:
        df['speed'].plot(kind='hist', bins=bins, alpha=0.5)
        plt_configure(figsize=(4, 3), title='Original speed distribution')
        print ' Too many zeros'
        too_many_zero = True
    return too_many_zero, null_wind_frequency


def randomize_angle(df, DIR_REDISTRIBUTE, sector_length = 10):
    if DIR_REDISTRIBUTE == 'even':
        df['dir_ran'] = df['dir'].apply(lambda x: (x + np.random.uniform(-sector_length/2,sector_length/2)))
    else:
        df['dir_ran'] = df['dir'].apply(lambda x: (x + np.random.uniform(0,sector_length)))

    bins=arange(0, 360+10, 5)
    df['dir'].hist(bins=bins, alpha=0.5, label='Original Data')
    bins=arange(0, 360+10, 1)
    df['dir_ran'].hist(bins=bins, alpha=0.5, label='Redistributed Data')
    plt_configure(xlabel="Direction", ylabel="Frequency", tight='x',
                  legend={'loc':'best'}, figsize=(8, 3))

    df['dir']=df['dir_ran']
    df.drop(['dir_ran'], 1,inplace=True)
    return df


def randomize_speed(df, with_too_many_zero):
    # Round down speed, need more caution
    if not with_too_many_zero:
        speed_redistribution_info = 'Redistribute upward, e.g. 0 -> [0,1]'
        df['speed_ran'] = df['speed'].apply(lambda x: (x + np.random.uniform(0,1)))
    else:
        speed_redistribution_info = 'Redistribute downward, e.g. 1 -> [0,1]'
        df['speed_ran'] = df['speed'].apply(lambda x: (x + np.random.uniform(-1,0)) if x > 0 else x)

    max_speed = df.speed.max()
    df['speed'].hist(bins=arange(0, max_speed), alpha=0.5, label='Original Data')
    df['speed_ran'].hist(bins=arange(0, max_speed, 0.5), alpha=0.5, label='Redistributed Data')
    print speed_redistribution_info
    plt_configure(xlabel="Speed", ylabel="Frequency", legend=True, figsize=(8, 3))

    df['speed']=df['speed_ran']
    df.drop(['speed_ran'], 1,inplace=True)
    return df, speed_redistribution_info