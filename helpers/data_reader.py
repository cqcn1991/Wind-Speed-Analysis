from .shared_imports import *


def read_cn_database(file_path):
    df = pd.read_csv(file_path,skipinitialspace=True, skiprows=[0])
    df.columns = ['station_number', 'year', 'month', 'day','HrMn','dir','speed']
    df.drop(['station_number'], 1,inplace=True)

    from datetime import datetime
    df['date'] = df.apply(lambda x: datetime.strptime("{0} {1} {2}".format(x['year'], x['month'], x['day']), "%Y %m %d"),
                            axis=1)
    df['date']=df['date'].apply(lambda x: int(x.strftime("%Y%m%d")))
    df['HrMn']=df['HrMn'].apply(lambda x: x*100)
    df.drop(['year', 'month', 'day'], 1, inplace=True)
    cols = df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df = df[cols]
    df['type'] = 'default'
    df['wind_type'] = 'default'
    return df
