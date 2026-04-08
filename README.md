# TradingBot

## Overview

TradingBot is a modular Python-based trading system designed for market data analysis and automated trading workflows.

Unlike simple script-based bots, this project is structured with separated components for exchange integration, execution logic, strategy management, configuration, and testing.

---

## Architecture

The system is organized into multiple modules:

* `exchanges/` → API integration (e.g., Binance)
* `execution/` → order handling and trade execution logic
* `strategies/` → signal generation, event detection, and strategy selection
* `models/` → experimental components (including reinforcement learning modules)
* `config/` → API keys, trading rules, logging, and database settings
* `tests/` → validation for API, execution, strategies, and WebSocket behavior
* `dashboard/`, `notification/`, `utils/` → supporting components

This structure allows easier extension, testing, and future scaling.

---

## Core Features

* Modular trading system design
* Binance API integration
* Strategy-based trading workflow
* Risk management and signal generation modules
* Environment-based execution (test vs production)
* Basic test coverage for key components

---

## Current Behavior

* Initializes trading workflow using Binance API
* Runs market analysis loop (default: BTCUSDT)
* Executes logic based on selected strategy modules
* Operates in safe test mode by default

---

## Environment Configuration

### Test Mode

* Trading disabled
* Uses test API
* `.env.test`

### Production Mode

* Trading enabled
* Uses live API
* `.env.prod`

> Trading will not execute unless `AUTO_TRADING=true` is set.

---

## Limitations

* Live trading is currently disabled by default
* 일부 전략 및 모델은 실험 단계
* Full error-case coverage not yet implemented
* Real-time streaming (WebSocket) is not fully integrated

---

## Future Improvements

* Full WebSocket-based real-time data handling
* Expanded testing coverage
* Strategy performance evaluation and optimization
* Safer production execution controls


