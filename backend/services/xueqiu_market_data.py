"""
雪球行情数据服务
提供从雪球获取实时股票行情数据的功能
"""

import requests
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 全局cookie配置变量
_xueqiu_cookie_string: Optional[str] = None


class XueqiuMarketData:
    """雪球行情数据服务类"""

    def __init__(self):
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self):
        """设置请求会话的cookies和headers"""
        # 尝试从全局变量获取cookie配置
        cookie_string = self._get_cookie_from_global()


        cookies = self._parse_cookie_string(cookie_string)

        # 设置会话的cookies和headers
        self.session.cookies.update(cookies)

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'https://xueqiu.com',
            'priority': 'u=1, i',
            'referer': 'https://xueqiu.com/S/MSFT',
            'sec-ch-ua': '"Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',
        }
        self.session.headers.update(headers)

    def _get_cookie_from_global(self):
        """从全局变量获取cookie配置"""
        global _xueqiu_cookie_string
        return _xueqiu_cookie_string

    def _parse_cookie_string(self, cookie_string: str) -> dict:
        """解析cookie字符串为字典"""
        cookies = {}
        try:
            if not cookie_string or not cookie_string.strip():
                return cookies

            # 处理不同格式的cookie字符串
            if '; ' in cookie_string:
                # 格式: "key1=value1; key2=value2"
                for cookie in cookie_string.split('; '):
                    if '=' in cookie:
                        key, value = cookie.split('=', 1)
                        cookies[key.strip()] = value.strip()
            elif '\n' in cookie_string:
                # 格式: 每行一个cookie
                for line in cookie_string.strip().split('\n'):
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        cookies[key.strip()] = value.strip()
            else:
                # 单个cookie
                if '=' in cookie_string:
                    key, value = cookie_string.split('=', 1)
                    cookies[key.strip()] = value.strip()
        except Exception as e:
            logger.error(f"解析cookie字符串失败: {e}")

        return cookies

    def update_cookies(self, cookie_string: str):
        """更新会话的cookies"""
        try:
            new_cookies = self._parse_cookie_string(cookie_string)
            if new_cookies:
                self.session.cookies.update(new_cookies)
                logger.info("雪球cookie已更新")
            else:
                logger.warning("解析cookie字符串为空")
        except Exception as e:
            logger.error(f"更新cookie失败: {e}")

    def get_kline_data(self, symbol: str, period: str = '1m', count: int = 100) -> Optional[Dict[str, Any]]:
        """
        获取K线数据

        Args:
            symbol: 股票Symbol，如 'MSFT'
            period: 时间周期，如 '1m', '5m', '15m', '30m', '1h', '1d'
            count: 获取数据条数，负数表示获取最新的数据

        Returns:
            包含K线数据的字典，失败返回None
        """
        try:
            # 当前时间戳（毫秒）
            current_timestamp = int(time.time() * 1000)

            # 构建请求URL
            url = 'https://stock.xueqiu.com/v5/stock/chart/kline.json'
            # 修正period参数 - 雪球API使用的格式
            api_period = period
            if period == '1d':
                api_period = 'day'
            elif period == '1m':
                api_period = 'minute'

            params = {
                'symbol': symbol,
                'begin': current_timestamp,
                'period': api_period,
                'type': 'before',
                'count': -abs(count),  # 使用负数获取最新数据
                'indicator': 'kline'  # 简化indicator参数
            }

            logger.info(f"请求雪球API: {url} with params: {params}")

            response = self.session.get(url, params=params, timeout=15)  # 增加超时时间

            # 检查HTTP状态码
            if response.status_code != 200:
                logger.error(f"HTTP错误 {response.status_code}: {response.text[:200]}")
                return None

            data = response.json()

            # 更详细的错误检查
            if data.get('error_code') == 0 or 'data' in data:
                # 检查数据是否有效
                if 'data' in data and data['data'] and data['data'].get('item'):
                    return data
                else:
                    logger.warning(f"雪球API返回空数据 for {symbol}: {data}")
                    return None
            else:
                error_code = data.get('error_code', 'unknown')
                error_desc = data.get('error_description', data.get('error_msg', ''))
                logger.error(f"雪球API错误 {error_code}: {error_desc}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"请求雪球API失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    if error_data.get('error_code') == '400016':
                        logger.error("雪球API返回400016错误，可能是cookie无效或过期")
                except:
                    pass
            return None
        except Exception as e:
            logger.error(f"解析雪球API数据失败: {e}")
            return None

    def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        获取最新价格

        Args:
            symbol: 股票Symbol

        Returns:
            最新价格，失败返回None
        """
        # 优先尝试股票信息API获取实时价格
        try:
            url = 'https://stock.xueqiu.com/v5/stock/quote.json'
            params = {'symbol': symbol, 'extend': 'detail'}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if 'data' in data and 'quote' in data['data']:
                current_price = data['data']['quote'].get('current')
                if current_price and float(current_price) > 0:
                    logger.info(f"从雪球股票信息API获取 {symbol} 价格: ${current_price}")
                    return float(current_price)
        except Exception as e:
            logger.warning(f"股票信息API获取 {symbol} 价格失败: {e}")

        # 备用方案：尝试K线数据
        kline_data = self.get_kline_data(symbol, period='day', count=1)

        if not kline_data or 'data' not in kline_data:
            logger.warning(f"无法获取 {symbol} 的日线K线数据")
            return None

        data = kline_data['data']

        # 检查数据结构
        items = data.get('item', [])
        if not items or len(items) == 0:
            logger.warning(f"{symbol} 返回空数据，可能市场已关闭或symbol不正确")
            return None

        # 获取最新的一条数据
        latest_item = items[0]

        # 根据column找到close价格的索引
        columns = data.get('column', [])
        if 'close' in columns:
            close_index = columns.index('close')
            if len(latest_item) > close_index:
                price = latest_item[close_index]
                if price and float(price) > 0:
                    logger.info(f"从雪球K线API获取 {symbol} 价格: ${price}")
                    return float(price)

        logger.error(f"无法从 {symbol} 数据中提取有效价格")
        return None

    def parse_kline_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        解析K线数据为标准格式

        Args:
            raw_data: 从雪球API获取的原始数据

        Returns:
            解析后的K线数据列表
        """
        if not raw_data or 'data' not in raw_data:
            return []

        data = raw_data['data']
        columns = data.get('column', [])
        items = data.get('item', [])

        if not columns or not items:
            return []

        # 创建列名到索引的映射
        column_map = {col: i for i, col in enumerate(columns)}

        parsed_data = []

        for item in items:
            kline_dict = {}

            # 解析各个字段
            if 'timestamp' in column_map and len(item) > column_map['timestamp']:
                kline_dict['timestamp'] = item[column_map['timestamp']]
                kline_dict['datetime'] = datetime.fromtimestamp(item[column_map['timestamp']] / 1000)

            for field in ['open', 'high', 'low', 'close', 'volume', 'amount']:
                if field in column_map and len(item) > column_map[field]:
                    value = item[column_map[field]]
                    kline_dict[field] = float(value) if value is not None else None

            # 涨跌幅相关
            for field in ['chg', 'percent']:
                if field in column_map and len(item) > column_map[field]:
                    value = item[column_map[field]]
                    kline_dict[field] = float(value) if value is not None else None

            parsed_data.append(kline_dict)

        return parsed_data

    def get_market_status(self, symbol: str) -> Dict[str, Any]:
        """
        获取市场状态信息

        Args:
            symbol: 股票Symbol

        Returns:
            市场状态信息
        """
        # 简单实现，基于时间判断市场状态
        # 实际项目中可以调用更详细的API
        current_time = datetime.now()
        hour = current_time.hour

        # 美股交易时间判断（简化版）
        if 21 <= hour <= 23 or 0 <= hour <= 4:  # 美股交易时间（北京时间）
            market_status = "TRADING"
        else:
            market_status = "CLOSED"

        return {
            "symbol": symbol,
            "market_status": market_status,
            "timestamp": int(time.time() * 1000),
            "current_time": current_time.isoformat()
        }


# 创建全局实例
xueqiu_client = XueqiuMarketData()


def get_last_price_from_xueqiu(symbol: str, market: str = "US") -> float:
    """
    从雪球获取最新价格

    Args:
        symbol: 股票Symbol
        market: 市场Symbol

    Returns:
        最新价格

    Raises:
        Exception: 当无法获取价格时抛出异常
    """
    price = xueqiu_client.get_latest_price(symbol)
    if price is None or price <= 0:
        raise Exception(f"无法获取 {symbol} 的有效价格")
    return price


def get_kline_data_from_xueqiu(symbol: str, period: str = '1m', count: int = 100) -> List[Dict[str, Any]]:
    """
    从雪球获取K线数据

    Args:
        symbol: 股票Symbol
        period: 时间周期
        count: 数据条数

    Returns:
        K线数据列表

    Raises:
        Exception: 当无法获取K线数据时抛出异常
    """
    raw_data = xueqiu_client.get_kline_data(symbol, period, count)
    if not raw_data:
        raise Exception(f"无法获取 {symbol} 的K线数据")

    kline_data = xueqiu_client.parse_kline_data(raw_data)
    if not kline_data:
        raise Exception(f"解析 {symbol} 的K线数据失败")

    return kline_data


def set_xueqiu_cookie(cookie_string: str):
    """
    设置雪球cookie全局变量

    Args:
        cookie_string: 新的cookie字符串
    """
    global _xueqiu_cookie_string
    _xueqiu_cookie_string = cookie_string.strip() if cookie_string else None
    logger.info(f"雪球cookie已更新，长度: {len(_xueqiu_cookie_string) if _xueqiu_cookie_string else 0}")


def get_xueqiu_cookie() -> Optional[str]:
    """
    获取当前雪球cookie配置

    Returns:
        当前的cookie字符串，如果未设置则返回None
    """
    global _xueqiu_cookie_string
    return _xueqiu_cookie_string


def update_xueqiu_cookie(cookie_string: str):
    """
    更新雪球客户端的cookie配置

    Args:
        cookie_string: 新的cookie字符串
    """
    global xueqiu_client

    # 设置全局变量
    set_xueqiu_cookie(cookie_string)

    # 重新设置客户端会话
    xueqiu_client._setup_session()

    logger.info(f"雪球客户端cookie已更新并重新初始化")