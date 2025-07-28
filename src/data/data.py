import pandas as pd
import os
from constants import Timeframe, Asset
from data.api import coindesk_api
from typing import Literal
from constants import EARLIEST_BACKTEST_DATE
from datetime import datetime

def get_df(asset: Asset, timeframe: Timeframe, path_append: str ="", file_type: Literal['PKL', 'CSV', 'PARQUET'] = 'PARQUET') -> pd.DataFrame:
    ext = file_type.lower()
    source_dir = path_append + f"./src/data/{ ext }/"

    for file in os.scandir(source_dir):
        if asset.name in file.path and timeframe.name in file.path:
            match file_type:
                case 'PKL':
                    return pd.read_pickle(file.path)
                case 'CSV':
                    return pd.read_csv(file.path)
                case 'PARQUET':
                    return pd.read_parquet(file.path)
                
    df = coindesk_api.get_OHLC(
        from_date=EARLIEST_BACKTEST_DATE,
        to_date=datetime.now(),
        asset=asset,
        timeframe=timeframe)
    
    if df is not None:
        return df
            
    raise FileNotFoundError("Could not find file: {pair}-{timeframe.name}")

def save_df(df: pd.DataFrame, file_name: str, path_append: str ="", file_type: Literal['PKL', 'CSV', 'PARQUET'] = 'PARQUET'):
    ext = file_type.lower()
    dest_dir = os.path.join(path_append, f"./src/data/{ ext }/")
    os.makedirs(dest_dir, exist_ok=True)

    match file_type:
        case 'PKL':
            df.to_pickle(os.path.join(dest_dir, f"{file_name}.pkl"))
        case 'CSV':
            df.to_csv(os.path.join(dest_dir, f"{file_name}.csv"))
        case 'PARQUET':
            df.to_parquet(os.path.join(dest_dir, f"{file_name}.parquet"))