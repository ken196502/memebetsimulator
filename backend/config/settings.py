from pydantic import BaseModel
from typing import Dict, Optional
import os


class MarketConfig(BaseModel):
    market: str
    min_commission: float
    commission_rate: float
    exchange_rate: float
    min_order_quantity: int = 1
    lot_size: int = 1


# Demo default configs for PUMP (pump.fun meme coins)
DEFAULT_TRADING_CONFIGS: Dict[str, MarketConfig] = {
    "PUMP": MarketConfig(
        market="PUMP",
        min_commission=0.01,  # Low commission for meme coins
        commission_rate=0.003,  # 0.3% commission rate
        exchange_rate=1.0,
        min_order_quantity=1,
        lot_size=1,
    ),
    # Keep US and HK for backward compatibility
    "US": MarketConfig(
        market="US",
        min_commission=1.0,
        commission_rate=0.0005,
        exchange_rate=1.0,
        min_order_quantity=1,
        lot_size=1,
    ),
    "HK": MarketConfig(
        market="HK",
        min_commission=20.0,
        commission_rate=0.00027,
        exchange_rate=7.8,
        min_order_quantity=100,
        lot_size=100,
    ),
}


def get_pump_fun_cookie() -> Optional[str]:
    """Get pump.fun cookie from file or environment"""
    # Try to read from config file first
    try:
        cookie_file_path = os.path.join(os.path.dirname(__file__), "pump_cookies.txt")
        if os.path.exists(cookie_file_path):
            with open(cookie_file_path, 'r', encoding='utf-8') as f:
                cookie_content = f.read().strip()
                if cookie_content:
                    return cookie_content
    except Exception as e:
        print(f"Failed to read pump_cookies.txt: {e}")
    
    # Fallback to environment variable
    return os.getenv("PUMP_FUN_COOKIE")
