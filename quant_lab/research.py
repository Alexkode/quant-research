import json
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

FEATURES=['return1','return5','return20','vol10','trend','range','volume_change','day_sin','day_cos']
def features(bars):
    frames=[]
    for symbol,g in bars.groupby('symbol'):
        g=g.sort_values('date').copy();r=g.close.pct_change()
        g['return1']=r;g['return5']=g.close.pct_change(5);g['return20']=g.close.pct_change(20)
        g['vol10']=r.rolling(10).std();g['trend']=g.close/g.close.rolling(30).mean()-1
        g['range']=(g.high-g.low)/g.open;g['volume_change']=np.log1p(g.volume).diff()
        g['day_sin']=np.sin(2*np.pi*g.date.dt.dayofweek/7);g['day_cos']=np.cos(2*np.pi*g.date.dt.dayofweek/7)
        # Features known at today's close. Trade enters tomorrow's open, exits tomorrow's close.
        g['target_return']=(g.close/g.open-1).shift(-1);g['target_date']=g.date.shift(-1)
        frames.append(g)
    return pd.concat(frames).replace([np.inf,-np.inf],np.nan).dropna(subset=FEATURES+['target_return','target_date'])

def walk_forward(frame,year,c):
    predictions=[];folds=[]
    for month in range(1,13):
        start=pd.Timestamp(year=year,month=month,day=1,tz='UTC');end=start+pd.offsets.MonthBegin(1)
        # Training labels finish strictly before test feature availability.
        train=frame[(frame.target_date<start-pd.Timedelta(days=1)) & (frame.date>=start-pd.Timedelta(days=366))]
        test=frame[(frame.target_date>=start)&(frame.target_date<end)]
        if len(train)<100 or test.empty:continue
        assert train.target_date.max()<test.date.min()
        model=make_pipeline(StandardScaler(),LogisticRegression(C=c,max_iter=500,random_state=2027))
        model.fit(train[FEATURES],train.target_return>0)
        out=test[['date','target_date','symbol','target_return','trend']].copy();out['probability']=model.predict_proba(test[FEATURES])[:,1];predictions.append(out)
        folds.append({'test_start':str(start),'train_label_end':str(train.target_date.max()),'first_test_feature_time':str(test.date.min()),'train_rows':len(train),'test_rows':len(test)})
    return pd.concat(predictions).sort_values(['target_date','symbol']),folds

def daily_returns(pred,threshold,fee_bps):
    position=(pred.probability>=threshold).astype(float)
    net=position*pred.target_return-2*fee_bps/10000*position
    return pd.DataFrame({'date':pred.target_date,'net':net}).groupby('date').net.mean()

def stats(values):
    x=np.asarray(values);equity=np.cumprod(1+x);peak=np.maximum.accumulate(np.r_[1.,equity])[1:]
    rng=np.random.default_rng(2027);means=[]
    for _ in range(1000):
        starts=rng.integers(0,len(x),size=int(np.ceil(len(x)/7)));idx=np.concatenate([(s+np.arange(7))%len(x) for s in starts])[:len(x)];means.append(x[idx].mean())
    return {'days':len(x),'total_return':float(equity[-1]-1),'cagr':float(equity[-1]**(365/len(x))-1),
            'sharpe_365':float(np.sqrt(365)*x.mean()/x.std(ddof=1)) if x.std()>0 else 0,
            'max_drawdown':float(np.min(equity/peak-1)),'mean_daily_return_95_block_bootstrap':list(map(float,np.quantile(means,[.025,.975])))}

def main():
    bars=pd.read_parquet('data/bars.parquet');frame=features(bars);validation=[]
    for c in [.1,1,10]:
        pred,_=walk_forward(frame,2024,c)
        for threshold in [.5,.55,.6]:
            validation.append({'c':c,'threshold':threshold,'mean_net_return':float(daily_returns(pred,threshold,10).mean())})
    selected=max(validation,key=lambda r:r['mean_net_return']);pred,folds=walk_forward(frame,2025,selected['c'])
    pred['position']=(pred.probability>=selected['threshold']).astype(int)
    results={}
    for fee in [0,5,10,20]:results[f'fee_{fee}_bps_each_side']=stats(daily_returns(pred,selected['threshold'],fee))
    for name,pos in [('always_long_intraday',np.ones(len(pred))),('momentum', (pred.trend>0).astype(float))]:
        net=pos*pred.target_return-2*.001*pos;daily=pd.DataFrame({'date':pred.target_date,'net':net}).groupby('date').net.mean();results[name]=stats(daily)
    results['cash']=stats(np.zeros(pred.target_date.nunique()))
    for symbol,g in pred.groupby('symbol'):results[symbol]=stats(daily_returns(g,selected['threshold'],10))
    result={'data_period':'2022-2025','validation_period':2024,'test_period':2025,'selected':selected,'validation_candidates':validation,
            'test_auc':float(roc_auc_score(pred.target_return>0,pred.probability)),
            'test_trade_fraction':float(pred.position.mean()),'folds':folds,'results':results,
            'execution':'Long/flat only, decision at previous close, entry next open, exit same close. Equal notional BTC/ETH sleeves; daily rebalance. Cost charged on both entry and exit. No leverage, funding or interest. Perfect fills and price availability are simplifying assumptions.'}
    Path('results/research.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');pred.to_csv('results/test-predictions.csv',index=False);print(json.dumps({'selected':selected,'test_auc':result['test_auc'],'net':results['fee_10_bps_each_side']}))

if __name__=='__main__':main()
