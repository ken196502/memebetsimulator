from typing import Dict, List, Any
import logging
from .xueqiu_market_data import (
    get_last_price_from_xueqiu,
    get_kline_data_from_xueqiu,
    xueqiu_client,
    get_xueqiu_cookie,
)
from .pump_fun_market_data import (
    get_last_price_from_pump_fun,
    get_pump_fun_coin,
    get_pump_fun_coins,
    pump_fun_client,
    get_pump_fun_cookie,
)

logger = logging.getLogger(__name__)


def _check_xueqiu_cookie_available() -> bool:
    cookie = get_xueqiu_cookie()
    return bool(cookie and cookie.strip())


def _check_pump_fun_cookie_available() -> bool:
    cookie = get_pump_fun_cookie()
    return bool(cookie and cookie.strip())


def get_last_price(symbol: str, market: str) -> float:
    """Get last price for symbol from appropriate market data source"""
    key = f"{symbol}.{market}"
    logger.info(f"正在获取 {key} 的实时价格...")

    if market.upper() == "PUMP":
        # Use pump.fun for meme coins
        try:
            price = get_last_price_from_pump_fun(symbol)
            if price and price > 0:
                logger.info(f"从Pump.fun获取 {key} 实时价格: {price}")
                return price
            raise Exception(f"Pump.fun返回无效价格: {price}")
        except Exception as pump_err:
            logger.error(f"从Pump.fun获取价格失败: {pump_err}")
            raise Exception(f"无法获取 {key} 的实时价格: {pump_err}")
    else:
        # Use xueqiu for traditional stocks
        try:
            price = get_last_price_from_xueqiu(symbol, market)
            if price and price > 0:
                logger.info(f"从雪球获取 {key} 实时价格: {price}")
                return price
            raise Exception(f"雪球返回无效价格: {price}")
        except Exception as xq_err:
            logger.error(f"从雪球获取价格失败: {xq_err}")
            raise Exception(f"无法获取 {key} 的实时价格: {xq_err}")


def get_kline_data(symbol: str, market: str, period: str = "1d", count: int = 100) -> List[Dict[str, Any]]:
    """Get kline data - pump.fun doesn't support klines, so return empty for PUMP market"""
    key = f"{symbol}.{market}"

    if market.upper() == "PUMP":
        # Pump.fun doesn't provide kline data, return empty list
        logger.info(f"Pump.fun不支持K线数据，返回空数据: {key}")
        return []

    try:
        data = get_kline_data_from_xueqiu(symbol, period, count)
        if data:
            logger.info(f"从雪球获取 {key} K线数据，共 {len(data)} 条")
            return data
        raise Exception("雪球返回空的K线数据")
    except Exception as xq_err:
        logger.error(f"从雪球获取K线数据失败: {xq_err}")
        raise Exception(f"无法获取 {key} 的K线数据: {xq_err}")


def get_market_status(symbol: str, market: str) -> Dict[str, Any]:
    """Get market status"""
    key = f"{symbol}.{market}"

    if market.upper() == "PUMP":
        # Pump.fun is always "open" since it's 24/7
        logger.info(f"Pump.fun市场状态: 24/7开放")
        return {
            "market_status": "OPEN",
            "market_name": "Pump.fun",
            "trading_hours": "24/7"
        }

    try:
        status = xueqiu_client.get_market_status(symbol)
        logger.info(f"从雪球获取 {key} 市场状态: {status.get('market_status')}")
        return status
    except Exception as xq_err:
        logger.error(f"获取市场状态失败: {xq_err}")
        raise Exception(f"无法获取 {key} 的市场状态: {xq_err}")


def get_pump_fun_trending_coins(limit: int = 20) -> List[Dict[str, Any]]:
    """Get trending pump.fun coins"""
    try:
        coins = pump_fun_client.get_trending_coins(limit=limit)
        logger.info(f"获取到 {len(coins)} 个热门Pump.fun代币")
        return coins
    except Exception as e:
        logger.error(f"获取热门代币失败: {e}")
        return []


def get_pump_fun_new_coins(limit: int = 20) -> List[Dict[str, Any]]:
    """Get new pump.fun coins"""
    try:
        coins = pump_fun_client.get_new_coins(limit=limit)
        logger.info(f"获取到 {len(coins)} 个新Pump.fun代币")
        return coins
    except Exception as e:
        logger.error(f"获取新代币失败: {e}")
        return []
