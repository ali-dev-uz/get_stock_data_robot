import asyncio
import warnings
import aiofiles
import ta
from aiogram.types import InputFile
from twelvedata import TDClient
from data.config import TWELVE_API, TICKER, FILE_PATH, CHANNEL
from loader import dp

warnings.filterwarnings("ignore",
                        message="errors='ignore' is deprecated and will raise in a future version. Use to_numeric without passing `errors` and catch exceptions explicitly instead")


async def connect_api():
    td = TDClient(apikey=TWELVE_API)
    # Construct the necessary time series
    ts = td.time_series(
        symbol=TICKER,
        interval="1min",
        outputsize=750,
        timezone="Asia/Tashkent",
    )
    # pprint.pprint(ts.as_json()[0])
    ts = await ema_indicator(ts)  # EMA20, EMA50, EMA100, EMA200
    ts = await atr(ts)  # ATR14: Average True Range, a measure of volatility.
    ts = await adx(ts)  # ADX14: Average Directional Index, which measures the strength of a trend.
    ts = await rsi(
        ts)  # RSI 7: Relative Strength Index, a momentum oscillator. RSI 50: Relative Strength Index, a momentum oscillator.
    ts = await stoch(
        ts)  # Stochastic: Stochastic oscillator, which measures the position of a price relative to its recent highs and lows.
    all_data = await bollinger(ts)  # Bollinger_high: Upper Bollinger Band.Bollinger_low: Lower Bollinger Band.
    await write_to_csv(all_data)
    await send_message()


async def ema_indicator(ts):
    ema = ts.with_ema(time_period=20).with_ema(time_period=50).with_ema(time_period=100).with_ema(
        time_period=200)
    return ema


async def atr(ts):
    atr14 = ts.with_atr(time_period=14)
    return atr14


async def adx(ts):
    adx14 = ts.with_adx(time_period=14)
    return adx14


async def rsi(ts):
    rsi750 = ts.with_rsi(time_period=7, series_type='close').with_rsi(time_period=50, series_type='close')
    return rsi750


async def stoch(ts):
    stochastic = ts.with_stoch()
    return stochastic


async def ichimoku(ts):
    ich_indicator = ts.with_ichimoku()
    return ich_indicator


async def bollinger(ts):
    ichimoku_data = await ichimoku(ts)  # Ichiko: A Japanese indicator system used to assess trends and trading signals.
    json_data = ts.as_json()
    pandas_data = ichimoku_data.as_pandas()
    new_format = json_data  # Assuming json_data is a list of dictionaries and we need the first element
    # Calculate Bollinger Bands
    try:
        pandas_data['bollinger_high'] = ta.volatility.BollingerBands(pandas_data['close'], window=20,
                                                                     window_dev=2).bollinger_hband()
        pandas_data['bollinger_low'] = ta.volatility.BollingerBands(pandas_data['close'], window=20,
                                                                    window_dev=2).bollinger_lband()
    except Exception as err:
        print(err)
    # alls = pandas_data.iloc[-1]
    # pprint.pprint(alls)

    new_format = pandas_data.to_dict(orient='records')
    for n, m in enumerate(json_data):
        new_format[n]['datetime'] = m['datetime']
        await asyncio.sleep(0.001)
    return new_format


async def write_to_csv(data):
    csv_columns = [
        'timestamp', 'open', 'close', 'high', 'low', 'volume',
        'EMA20', 'EMA50', 'EMA100', 'EMA200',
        'Bollinger_high', 'Bollinger_low', 'ATR14', 'ADX14',
        'RSI_7', 'RSI_50', 'Stochastic', 'Ichimoku'
    ]
    async with aiofiles.open(FILE_PATH, mode='w') as f:
        header = ','.join(csv_columns) + '\n'
        await f.write(header)
        for i, input_data in enumerate(data):
            if i == 721:
                break
            else:
                stoch_t = {
                    'slow_d': f"{input_data['slow_d']}",
                    'slow_k': f"{input_data['slow_k']}"
                }
                ichik = {
                    'chikou_span': f'{input_data["chikou_span"]}',
                    'kijun_sen': f'{input_data["kijun_sen"]}',
                    'senkou_span_a': f'{input_data["senkou_span_a"]}',
                    'senkou_span_b': f'{input_data["senkou_span_b"]}',
                    'tenkan_sen': f'{input_data["tenkan_sen"]}'
                }
                write_data = [f"{input_data['datetime']}", f"{input_data['open']}", f"{input_data['close']}",
                              f"{input_data['high']}", f"{input_data['low']}", f"{input_data['volume']}",
                              f"{input_data['ema1']}", f"{input_data['ema2']}", f"{input_data['ema3']}",
                              f"{input_data['ema4']}", f"{input_data['bollinger_high']}",
                              f"{input_data['bollinger_low']}", f"{input_data['atr']}", f"{input_data['adx']}",
                              f"{input_data['rsi1']}", f"{input_data['rsi2']}", f"{stoch_t}", f"{ichik}"]
                header = ','.join(write_data) + '\n'
                await f.write(header)
            await asyncio.sleep(0.001)


async def send_message():
    await dp.bot.send_document(chat_id=CHANNEL,
                               document=InputFile(FILE_PATH))



"""
For example:
    {'adx': 24.86173,
     'atr': 0.19314,
     'bollinger_high': np.nan,
     'bollinger_low': np.nan,
     'chikou_span': 212.52,
     'close': 212.565,
     'datetime': '2024-06-15 00:58:00',
     'ema1': 212.17365,
     'ema2': 212.1252,
     'ema3': 212.10243,
     'ema4': 212.17916,
     'high': 212.58,
     'kijun_sen': 212.0039,
     'low': 212.49001,
     'open': 212.5,
     'rsi1': 75.68065,
     'rsi2': 55.51867,
     'senkou_span_a': 212.15,
     'senkou_span_b': 212.095,
     'slow_d': 96.53851,
     'slow_k': 98.70695,
     'tenkan_sen': 212.11,
     'volume': 479071},
"""
