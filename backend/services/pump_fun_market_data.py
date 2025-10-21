"""
Pump.fun market data service for fetching meme coin data
"""
import requests
import logging
from typing import Dict, List, Any, Optional
from backend.config.settings import get_pump_fun_cookie

logger = logging.getLogger(__name__)

# Global cookie variable
_pump_fun_cookie_string = None

class PumpFunMarketData:
    """Fetch and parse market data from pump.fun"""
    
    BASE_URL = "https://pump.fun"
    API_BASE = "https://frontend-api.pump.fun"
    
    def __init__(self):
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """Setup request session with cookies and headers"""
        # Try to get cookie from global variable
        cookie_string = self._get_cookie_from_global()
        
        if cookie_string:
            # Parse cookie string
            cookies = self._parse_cookie_string(cookie_string)
        else:
            # Use default empty cookies
            cookies = {}
            logger.info("No pump.fun cookie configured, API calls may fail")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/html',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://pump.fun/',
            'Origin': 'https://pump.fun',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
        }
        
        # Set session cookies and headers
        self.session.cookies.update(cookies)
        self.session.headers.update(headers)
        
        self.timeout = 30
    
    def _get_cookie_from_global(self):
        """Get cookie configuration from global variable"""
        global _pump_fun_cookie_string
        return _pump_fun_cookie_string
    
    def _parse_cookie_string(self, cookie_string: str) -> dict:
        """Parse cookie string into dictionary"""
        cookies = {}
        try:
            # Handle different cookie string formats
            if '; ' in cookie_string:
                # Format: "key1=value1; key2=value2"
                for cookie in cookie_string.split('; '):
                    if '=' in cookie:
                        key, value = cookie.split('=', 1)
                        cookies[key.strip()] = value.strip()
            elif '\n' in cookie_string:
                # Format: one cookie per line
                for line in cookie_string.strip().split('\n'):
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        cookies[key.strip()] = value.strip()
            else:
                # Single cookie
                if '=' in cookie_string:
                    key, value = cookie_string.split('=', 1)
                    cookies[key.strip()] = value.strip()
        except Exception as e:
            logger.error(f"Failed to parse cookie string: {e}")
        
        return cookies
    
    def update_cookies(self, cookie_string: str):
        """Update session cookies"""
        try:
            new_cookies = self._parse_cookie_string(cookie_string)
            if new_cookies:
                self.session.cookies.update(new_cookies)
                logger.info("Pump.fun cookies updated")
            else:
                logger.warning("Parsed cookie string is empty")
        except Exception as e:
            logger.error(f"Failed to update cookies: {e}")
    
    def close(self):
        """Close HTTP session"""
        self.session.close()
    
    def get_coins_list(
        self, 
        limit: int = 50,
        offset: int = 0,
        sort: str = "last_trade_timestamp",
        order: str = "DESC",
        include_nsfw: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Fetch list of tokens from pump.fun API
        
        Args:
            limit: Number of tokens to fetch (default 50)
            offset: Pagination offset
            sort: Sort field (last_trade_timestamp, market_cap, created_timestamp)
            order: ASC or DESC
            include_nsfw: Include NSFW tokens
            
        Returns:
            List of token dictionaries with market data
        """
        try:
            # Try the API endpoint first
            url = f"{self.API_BASE}/coins"
            params = {
                "offset": offset,
                "limit": limit,
                "sort": sort,
                "order": order,
                "includeNsfw": str(include_nsfw).lower()
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return self._normalize_api_response(data)
            
            logger.warning(f"API returned status {response.status_code}, response: {response.text[:200]}")
            
            # Try to get some sample data even if API fails
            if response.status_code == 530:
                logger.info("API returned 530, trying alternative approach or returning mock data for testing")
                return self._get_mock_coins_data(limit)
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching coins list: {e}")
            return []
    
    def get_coin_data(self, mint_address: str) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed data for a specific token
        
        Args:
            mint_address: Solana token mint address
            
        Returns:
            Token data dictionary or None
        """
        try:
            url = f"{self.API_BASE}/coins/{mint_address}"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json()
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching coin {mint_address}: {e}")
            return None
    
    def get_coin_trades(
        self, 
        mint_address: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent trades for a token
        
        Args:
            mint_address: Solana token mint address
            limit: Number of trades to fetch
            offset: Pagination offset
            
        Returns:
            List of trade dictionaries
        """
        try:
            url = f"{self.API_BASE}/trades/{mint_address}"
            params = {
                "limit": limit,
                "offset": offset
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json()
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching trades for {mint_address}: {e}")
            return []
    
    def _normalize_api_response(self, data: Any) -> List[Dict[str, Any]]:
        """Normalize API response to consistent format"""
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'data' in data:
            return data['data']
        elif isinstance(data, dict) and 'coins' in data:
            return data['coins']
        return []
    
    def _parse_market_cap(self, text: str) -> float:
        """Parse market cap string like '$1.8M' or '$13.52K'"""
        text = text.strip().replace('$', '').replace(',', '')
        
        if 'M' in text:
            return float(text.replace('M', '')) * 1_000_000
        elif 'K' in text:
            return float(text.replace('K', '')) * 1_000
        
        try:
            return float(text)
        except:
            return 0.0
    
    def _parse_percentage(self, text: str) -> float:
        """Parse percentage string like '+65.10%' or '-25.05%'"""
        text = text.strip().replace('%', '').replace('+', '')
        
        try:
            return float(text)
        except:
            return 0.0
    
    def _get_mock_coins_data(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return mock coins data for testing when API is unavailable"""
        mock_coins = [
            {
                "mint": "11111111111111111111111111111112",
                "name": "TestCoin",
                "symbol": "TEST",
                "description": "A test meme coin for simulation",
                "image_uri": "https://via.placeholder.com/100",
                "usd_market_cap": 100000.0,
                "total_supply": 1000000000,
                "created_timestamp": 1700000000,
                "last_trade_timestamp": 1700001000,
                "nsfw": False,
                "complete": False
            },
            {
                "mint": "22222222222222222222222222222223",
                "name": "MoonDoge",
                "symbol": "MDOGE",
                "description": "Going to the moon with this doge",
                "image_uri": "https://via.placeholder.com/100",
                "usd_market_cap": 250000.0,
                "total_supply": 1000000000,
                "created_timestamp": 1700000100,
                "last_trade_timestamp": 1700001100,
                "nsfw": False,
                "complete": False
            },
            {
                "mint": "33333333333333333333333333333334",
                "name": "PepeCoin",
                "symbol": "PEPE",
                "description": "Rare pepe meme coin",
                "image_uri": "https://via.placeholder.com/100",
                "usd_market_cap": 500000.0,
                "total_supply": 1000000000,
                "created_timestamp": 1700000200,
                "last_trade_timestamp": 1700001200,
                "nsfw": False,
                "complete": False
            }
        ]
        
        return mock_coins[:limit]
    
    def get_trending_coins(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch trending coins (high volume, recent activity)
        """
        coins = self.get_coins_list(
            limit=limit,
            sort="last_trade_timestamp",
            order="DESC"
        )
        
        return coins
    
    def get_new_coins(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch recently created coins
        """
        coins = self.get_coins_list(
            limit=limit,
            sort="created_timestamp",
            order="DESC"
        )
        
        return coins
    
    def get_top_by_market_cap(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch coins with highest market cap
        """
        coins = self.get_coins_list(
            limit=limit,
            sort="market_cap",
            order="DESC"
        )
        
        return coins


# Create global instance
pump_fun_client = PumpFunMarketData()


# Convenience functions for easy usage
def get_pump_fun_coins(limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch pump.fun coins list"""
    return pump_fun_client.get_coins_list(limit=limit)


def get_pump_fun_coin(mint_address: str) -> Optional[Dict[str, Any]]:
    """Fetch single pump.fun coin data"""
    return pump_fun_client.get_coin_data(mint_address)


def get_pump_fun_cookie() -> Optional[str]:
    """Get pump.fun cookie from configuration"""
    try:
        from backend.repositories.config_repo import get_system_config
        config = get_system_config("pump_fun_cookie")
        return config.value if config else None
    except Exception as e:
        logger.error(f"Failed to get pump.fun cookie: {e}")
        return None


def set_pump_fun_cookie(cookie_string: str):
    """Set pump.fun cookie globally"""
    global _pump_fun_cookie_string
    _pump_fun_cookie_string = cookie_string
    pump_fun_client.update_cookies(cookie_string)


def initialize_pump_fun_client():
    """Initialize pump.fun client with stored cookie"""
    try:
        cookie = get_pump_fun_cookie()
        if cookie:
            set_pump_fun_cookie(cookie)
            logger.info("Pump.fun client initialized with stored cookie")
        else:
            logger.warning("No pump.fun cookie found in configuration")
    except Exception as e:
        logger.error(f"Failed to initialize pump.fun client: {e}")


# Get last price for compatibility with existing market data interface
def get_last_price_from_pump_fun(mint_address: str) -> float:
    """Get current price for a pump.fun token"""
    try:
        coin_data = get_pump_fun_coin(mint_address)
        if coin_data and 'usd_market_cap' in coin_data:
            # Calculate price from market cap and supply
            market_cap = coin_data.get('usd_market_cap', 0)
            supply = coin_data.get('total_supply', 1000000000)  # Default 1B tokens
            if supply > 0:
                return market_cap / supply
        
        # Fallback: if no coin data, check if it's a mock coin and return mock price
        mock_prices = {
            "11111111111111111111111111111112": 0.0001,  # TestCoin
            "22222222222222222222222222222223": 0.00025,  # MoonDoge
            "33333333333333333333333333333334": 0.0005,   # PepeCoin
        }
        if mint_address in mock_prices:
            return mock_prices[mint_address]
            
        return 0.0
    except Exception as e:
        logger.error(f"Error getting price for {mint_address}: {e}")
        return 0.0