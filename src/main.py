from loguru import logger
from data import data
from constants import Asset, Timeframe


@logger.catch
def main():
    df = data.get_df(
        pair=Asset.ADA_USD,
        timeframe=Timeframe.H1
    )
    print(df.head())


if __name__ == "__main__":
    main()