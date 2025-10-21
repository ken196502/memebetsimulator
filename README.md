# Pump.fun Meme Coin Trading Simulator

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pump.fun Meme Coin Trading Simulator is a real-time meme coin trading simulator with WebSocket-powered live updates. The project consists of:
- **Backend**: FastAPI server with WebSocket support for simulated pump.fun meme coin trading
- **Frontend**: React + TypeScript + TailwindCSS trading interface

## Development Commands

### Essential Commands
```bash
# Install all dependencies
pnpm install:all

# Development (runs both frontend and backend concurrently)
pnpm dev

# Individual services
pnpm dev:backend    # Runs backend on port 2611
pnpm dev:frontend   # Runs frontend on port 2621

# Build for production
pnpm build
```

### Backend Development
The backend uses uv for Python dependency management:
```bash
cd backend && uv sync --quiet  # Install dependencies
cd backend && uv run <command> # Run commands in venv
```

### Testing and Linting
The backend includes pytest, black, and ruff for quality assurance:
```bash
cd backend && uv run pytest          # Run tests
cd backend && uv run black .         # Format code
cd backend && uv run ruff check .    # Lint code
```

## Architecture Overview

### Backend Architecture
- **Main Entry**: `backend/main.py` - FastAPI application with CORS, WebSocket endpoint, and static file serving
- **WebSocket**: `backend/api/ws.py` - Real-time trading simulator with order matching
- **Database**: SQLAlchemy models in `backend/database/models.py` with PostgreSQL-ready schema
- **Services**: Business logic in `backend/services/` including market data, order matching, and asset calculation
- **Repositories**: Data access layer in `backend/repositories/`
- **API Routes**: RESTful endpoints in `backend/api/`

### Frontend Architecture
- **Main Component**: `frontend/app/main.tsx` - Single-page application with WebSocket singleton
- **Real-time Data**: WebSocket connections handle live position updates, order status, and trades
- **UI Components**: Modular components in `frontend/app/components/` with Radix UI primitives
- **Key Views**: Portfolio, Trading Panel, Asset Curve, and Ranking Table
- **Styling**: TailwindCSS with custom components in `frontend/app/components/ui/`

### WebSocket Protocol
The simulator uses a custom WebSocket protocol for real-time trading:
- **Bootstrap**: Creates/gets user with initial capital
- **Order Management**: Place orders with instant status updates
- **Snapshot Requests**: Fetch current portfolio state
- **Live Updates**: Automatic position value calculations and trade executions

## Key Features

### Trading Simulator
- Real-time order placement and execution
- Portfolio tracking with position P&L
- Commission calculation (1% of trade value, minimum $1)
- Market data integration with price updates

### User Management
- Automatic demo user creation
- Session-based authentication
- Multiple user support via WebSocket connections

### Market Data
- Real-time price updates (simulated)
- Position market value calculations
- Historical trade data storage

## Database Schema

The trading simulator uses these core models:
- **Users**: Account management with USD balance tracking
- **Positions**: Holdings with average cost basis
- **Orders**: Pending and executed trades
- **Trades**: Completed transactions with commissions
- **TradingConfig**: Market-specific configuration (US/HK markets)

## Technical Highlights

- **WebSocket Singleton**: Prevents duplicate connections in React StrictMode
- **Order Matching**: Server-side order execution logic
- **Real-time Calculations**: Automatic position valuation and P&L
- **SPA Routing**: Backend serves frontend for React Router integration
- **CORS-enabled**: Full cross-origin support for development

## Development Notes

- Backend runs on port 2611, frontend on port 2621
- WebSocket connects to `/ws` endpoint on backend
- Frontend proxies API calls to backend during development
- Uses uv for Python dependency management (similar to poetry)
- FastAPI serves static frontend files for production deployment