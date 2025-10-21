"""
API routes for pump.fun meme coin data
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import logging

from backend.services.market_data import (
    get_pump_fun_trending_coins,
    get_pump_fun_new_coins,
    get_last_price,
)
from backend.services.pump_fun_market_data import (
    pump_fun_client,
    get_pump_fun_coin,
    get_pump_fun_coins,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pump", tags=["pump-fun"])


@router.get("/coins")
async def get_coins(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort: str = Query("last_trade_timestamp", regex="^(last_trade_timestamp|market_cap|created_timestamp)$"),
    order: str = Query("DESC", regex="^(ASC|DESC)$"),
    include_nsfw: bool = Query(False)
) -> Dict[str, Any]:
    """Get list of pump.fun coins"""
    try:
        coins = pump_fun_client.get_coins_list(
            limit=limit,
            offset=offset,
            sort=sort,
            order=order,
            include_nsfw=include_nsfw
        )
        
        return {
            "success": True,
            "data": coins,
            "count": len(coins),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Failed to get coins: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch coins: {str(e)}")


@router.get("/coins/{mint_address}")
async def get_coin_detail(mint_address: str) -> Dict[str, Any]:
    """Get detailed data for a specific pump.fun coin"""
    try:
        coin_data = get_pump_fun_coin(mint_address)
        
        if not coin_data:
            raise HTTPException(status_code=404, detail=f"Coin {mint_address} not found")
        
        return {
            "success": True,
            "data": coin_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get coin {mint_address}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch coin data: {str(e)}")


@router.get("/coins/{mint_address}/trades")
async def get_coin_trades(
    mint_address: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
) -> Dict[str, Any]:
    """Get recent trades for a pump.fun coin"""
    try:
        trades = pump_fun_client.get_coin_trades(
            mint_address=mint_address,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "data": trades,
            "count": len(trades),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Failed to get trades for {mint_address}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch trades: {str(e)}")


@router.get("/coins/{mint_address}/price")
async def get_coin_price(mint_address: str) -> Dict[str, Any]:
    """Get current price for a pump.fun coin"""
    try:
        price = get_last_price(mint_address, "PUMP")
        
        if price <= 0:
            raise HTTPException(status_code=404, detail=f"Price not available for {mint_address}")
        
        return {
            "success": True,
            "data": {
                "mint_address": mint_address,
                "price": price,
                "market": "PUMP"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get price for {mint_address}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch price: {str(e)}")


@router.get("/trending")
async def get_trending(limit: int = Query(20, ge=1, le=50)) -> Dict[str, Any]:
    """Get trending pump.fun coins"""
    try:
        coins = get_pump_fun_trending_coins(limit=limit)
        
        return {
            "success": True,
            "data": coins,
            "count": len(coins)
        }
    except Exception as e:
        logger.error(f"Failed to get trending coins: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch trending coins: {str(e)}")


@router.get("/new")
async def get_new_coins(limit: int = Query(20, ge=1, le=50)) -> Dict[str, Any]:
    """Get newly created pump.fun coins"""
    try:
        coins = get_pump_fun_new_coins(limit=limit)
        
        return {
            "success": True,
            "data": coins,
            "count": len(coins)
        }
    except Exception as e:
        logger.error(f"Failed to get new coins: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch new coins: {str(e)}")


@router.get("/top")
async def get_top_by_market_cap(limit: int = Query(20, ge=1, le=50)) -> Dict[str, Any]:
    """Get top pump.fun coins by market cap"""
    try:
        coins = pump_fun_client.get_top_by_market_cap(limit=limit)
        
        return {
            "success": True,
            "data": coins,
            "count": len(coins)
        }
    except Exception as e:
        logger.error(f"Failed to get top coins: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch top coins: {str(e)}")


@router.get("/search")
async def search_coins(
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(20, ge=1, le=50)
) -> Dict[str, Any]:
    """Search pump.fun coins by name or symbol"""
    try:
        # Get all coins and filter by search query
        all_coins = pump_fun_client.get_coins_list(limit=200)
        
        # Simple text search in name, symbol, or description
        filtered_coins = []
        query_lower = q.lower()
        
        for coin in all_coins:
            name = coin.get('name', '').lower()
            symbol = coin.get('symbol', '').lower()
            description = coin.get('description', '').lower()
            
            if (query_lower in name or 
                query_lower in symbol or 
                query_lower in description):
                filtered_coins.append(coin)
                
                if len(filtered_coins) >= limit:
                    break
        
        return {
            "success": True,
            "data": filtered_coins,
            "count": len(filtered_coins),
            "query": q
        }
    except Exception as e:
        logger.error(f"Failed to search coins: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search coins: {str(e)}")