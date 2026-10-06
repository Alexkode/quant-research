import numpy as np,pandas as pd
from quant_lab.research import features,daily_returns

def synthetic():
    n=80;close=np.exp(np.linspace(0,1,n));return pd.DataFrame({'date':pd.date_range('2024-01-01',periods=n,tz='UTC'),'symbol':'TEST','open':close*.99,'high':close*1.01,'low':close*.98,'close':close,'volume':np.arange(n)+1})

def test_future_mutation_does_not_change_past_features():
    from quant_lab.research import FEATURES
    b=synthetic();before=features(b);b.loc[65:,'close']*=100;after=features(b)
    pd.testing.assert_frame_equal(before.loc[before.index<64,FEATURES],after.loc[after.index<64,FEATURES])

def test_target_is_next_day_and_round_trip_costs():
    f=features(synthetic());assert (f.target_date-f.date).eq(pd.Timedelta(days=1)).all()
    p=pd.DataFrame({'target_date':[pd.Timestamp('2025-01-01')],'probability':[.9],'target_return':[.01]})
    assert np.isclose(daily_returns(p,.5,10).iloc[0],.008)
