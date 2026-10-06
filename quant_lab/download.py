import argparse,asyncio,hashlib,io,json,zipfile
from pathlib import Path
import httpx,pandas as pd

COLUMNS=['timestamp','open','high','low','close','volume','close_time','quote_volume','trades','taker_base','taker_quote','ignore']
def parse(raw,symbol):
    frame=pd.read_csv(io.BytesIO(raw),header=None,names=COLUMNS)
    timestamps=frame.timestamp.astype('int64');unit='us' if timestamps.median()>1e14 else 'ms'
    frame['date']=pd.to_datetime(timestamps,unit=unit,utc=True);frame['symbol']=symbol
    return frame[['date','symbol','open','high','low','close','volume','quote_volume','trades']]

async def main(args):
    root=Path('data');root.mkdir(exist_ok=True);sem=asyncio.Semaphore(8);manifest=[];frames=[]
    async with httpx.AsyncClient(timeout=60,follow_redirects=True) as client:
        async def fetch(symbol,year,month):
            name=f'{symbol}-1d-{year}-{month:02d}.zip';url=f'https://data.binance.vision/data/spot/monthly/klines/{symbol}/1d/{name}'
            async with sem:
                path=root/name
                checksum=await client.get(url+'.CHECKSUM');checksum.raise_for_status();expected=checksum.text.split()[0]
                if not path.exists():
                    response=await client.get(url);response.raise_for_status();path.write_bytes(response.content)
                content=path.read_bytes();actual=hashlib.sha256(content).hexdigest()
                if actual!=expected:raise ValueError('Checksum mismatch: '+name)
                with zipfile.ZipFile(io.BytesIO(content)) as z:frame=parse(z.read(z.namelist()[0]),symbol)
                frames.append(frame);manifest.append({'url':url,'sha256':actual,'rows':len(frame),'timestamp_unit':'us' if year>=2025 else 'ms'})
        await asyncio.gather(*(fetch(s,y,m) for s in args.symbols for y in range(args.start,args.end+1) for m in range(1,13)))
    frame=pd.concat(frames).sort_values(['symbol','date']).reset_index(drop=True)
    if frame.duplicated(['symbol','date']).any():raise ValueError('Duplicate bars')
    for _,g in frame.groupby('symbol'):
        if not g.date.diff().dropna().eq(pd.Timedelta(days=1)).all():raise ValueError('Missing daily bars')
    frame.to_parquet(root/'bars.parquet',index=False)
    Path('results/manifest.json').write_text(json.dumps(sorted(manifest,key=lambda r:r['url']),indent=2)+'\n')
    print(f'Verified {len(manifest)} archives, {len(frame)} daily bars')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--start',type=int,default=2022);p.add_argument('--end',type=int,default=2025);p.add_argument('--symbols',nargs='+',default=['BTCUSDT','ETHUSDT']);asyncio.run(main(p.parse_args()))
