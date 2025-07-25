from constants import Asset
from constants import Timeframe
from datetime import datetime
from datetime import timedelta
import pandas as pd
from typing import Any, Literal
import requests
import time
from data.api.api_error import ApiError
from time import strftime, localtime
from data import data
from loguru import logger
from security.coindesk_key import API_kEY

BASE_URL = 'https://data-api.coindesk.com'
DATA_LIMIT = 2000


def make_request(
        path: str,
        params: dict[str, Any],
        headers: dict[str, Any],
        verb: Literal['GET', 'POST'] = 'GET',
        retry_on: list[int] = [429, 502, 503, 504],
        retry_delay: float = 2.0,
        retry_max: int = 3
) -> Any:
    url = f"{BASE_URL}{path}"
    logger.info(f"calling {url} with params: {params}")

    session = requests.Session()

    for attempt in range(1, retry_max + 1):
        try:
            response = session.request(method=verb, url=url, params=params, headers=headers)
        except (requests.ConnectionError, requests.ConnectTimeout) as e:
            logger.warning(f"[Attempt {attempt}] Connection error: {e}")
        else:
            if response.status_code in retry_on:
                logger.warning(f"[Attempt {attempt}] Retrying due to status code {response.status_code}")
            elif not 200 <= response.status_code < 300:
                raise ApiError(f"{url} returned {response.status_code}: {response.content}")
            else:
                logger.info(f"Success: {url}")
                return response.json()

        time.sleep(retry_delay * attempt)

    raise ApiError(f"Failed to get successful response from {url} after {retry_max} retries")



def get_OHLC(
        from_date: datetime,
        to_date: datetime = datetime.now().replace(minute=0,second=0,microsecond=0),
        asset: Asset = Asset.ADA_USD,
        timeframe: Timeframe = Timeframe.H1,
) -> pd.DataFrame|None:
    
    path_map = {
        Timeframe.D: "days",
        Timeframe.H1: "hours",
        Timeframe.M1: "minutes"
    }

    path = f"/index/cc/v1/historical/{path_map.get(timeframe, '')}"
    result = []

    logger.info(f"Pulling data from {from_date} to {to_date}")

    current = from_date
    while current < to_date:
        match timeframe:
            case Timeframe.D:
                chunk_end = min(current + timedelta(days=DATA_LIMIT), to_date)
            case Timeframe.M1:
                chunk_end = min(current + timedelta(minutes=DATA_LIMIT), to_date)
            case _:
                chunk_end = min(current + timedelta(hours=DATA_LIMIT), to_date)
        
        logger.info(f"Fetching chunk: {current} to {chunk_end}")
        ticks = int((chunk_end - current).total_seconds() / 60 / timeframe.value)
        instrument = asset.value.replace('_', '-')

        params = {
            "groups": "OHLC",
            "to_ts": chunk_end.timestamp(),
            "instrument": instrument,
            "limit": ticks,
            "market": "cadli",
            "aggregate": "1",
            "apply_mapping": "true",
            "response_format": "JSON",
            "fill": "true"
        }

        headers = {"Authorization": f"ApiKey {API_kEY}"}

        chunk = make_request(path=path, params=params, headers=headers)
        result += chunk.get('Data', [])
        current = chunk_end

    df = pd.DataFrame(result).rename(columns={
        'UNIT': 'timeframe',
        'TIMESTAMP': 'timestamp',
        'OPEN': 'open',
        'HIGH': 'high',
        'LOW': 'low',
        'CLOSE': 'close'
    }).drop(columns='timeframe')

    df['timestamp'] = df['timestamp'].apply(lambda x: strftime('%m-%d-%Y %H:%M', localtime(x)))

    file_name = f"{pair.value.replace('/', '_')}-{timeframe.name}-{from_date.strftime('%m-%d-%Y')}"
    data.save_df(df=df, file_name=file_name)

    return df

    # path = "/index/cc/v1/historical/"
    # match timeframe:
    #     case Timeframe.D:
    #         path += "days"
    #     case Timeframe.H1:
    #         path += "hours"
    #     case Timeframe.M1:
    #         path += "minutes"
    #     case _:
    #         path += ""

    # result = []
    # print(f"Pulling data from {from_date} to {to_date}")
    # current_date = from_date

    # while current_date < to_date:
    #     chunk_end = min(current_date + timedelta(hours=DATA_LIMIT), to_date)
    #     print(f"Current chunk end {chunk_end}")
    #     chunk_end_timestamp = chunk_end.timestamp()
    #     total_data_ticks = (chunk_end - current_date).total_seconds() / 60 / timeframe.value
    #     instrument = pair.value.replace('_', '-')
    #     params = {
    #         "groups": "OHLC",
    #         "to_ts": chunk_end_timestamp,
    #         "instrument": instrument,
    #         "limit": int(total_data_ticks),
    #         "market": "cadli",
    #         "aggregate": "1",
    #         "apply_mapping": "true",
    #         "response_format": "JSON",
    #         "fill": "true"
    #     }
    #     headers = {
    #         "Authorization": f"ApiKey {API_KEY}"
    #     }

    #     logger.info(f"making OHLC request")
    #     chunk_result = make_request(
    #         path=path,
    #         params=params,
    #         headers=headers
    #     )
        
    #     result += chunk_result['Data']

    #     current_date = chunk_end

    # df = pd.DataFrame(result)
    # df = df.rename(columns={
    #     'UNIT': 'timeframe', 
    #     'TIMESTAMP': 'timestamp', 
    #     'OPEN': 'open', 
    #     'HIGH': 'high', 
    #     'LOW': 'low', 
    #     'CLOSE': 'close'
    #     }, errors='raise').drop(['timeframe'], axis=1)
    
    # df['timestamp'] = df['timestamp'].apply(lambda x: strftime('%m-%d-%Y %H:%M', localtime(x)))

    # df_name = f"{ pair.value.replace('/', '_') }-{ timeframe.name }-{ from_date.strftime('%m-%d-%Y') }"
    # data.save_df(
    #     df=df,
    #     file_name=df_name
    # )