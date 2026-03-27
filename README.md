# Binance Futures Testnet Trading Bot

A clean, lightweight Python CLI bot for placing orders on the **Binance Futures Testnet (USDT-M)**.

---

## Features

- Place **MARKET**, **LIMIT**, and **STOP_MARKET** orders
- Supports **BUY** and **SELL** sides
- Full **input validation** with descriptive error messages
- **Structured logging** to `logs/trading_bot.log` (rotating, 5 MB × 3 backups)
- **Exception handling** for API errors, network failures, and invalid input
- Clean separation: `client.py` (API layer) / `orders.py` (business logic) / `cli.py` (CLI layer)

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API wrapper (signing, request, error handling)
│   ├── orders.py          # Order placement logic + formatted output
│   ├── validators.py      # Input validation
│   └── logging_config.py  # Rotating file + console logger
├── logs/
│   └── trading_bot.log    # Auto-created on first run (not committed)
├── cli.py               # argparse CLI entry point
├── .env.example         # Template for environment variables
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Setup

### 1. Prerequisites

- Python 3.8+
- A [Binance Futures Testnet](https://testnet.binancefuture.com) account
- API key and secret from the testnet dashboard

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set credentials

Copy the example env file and fill in your testnet credentials:

```bash
cp .env.example .env
```

Then edit `.env`:

```
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
```

> **Note:** `.env` is listed in `.gitignore` and will never be committed.

Alternatively, export them directly in your shell:

```bash
export BINANCE_API_KEY=your_testnet_api_key
export BINANCE_API_SECRET=your_testnet_api_secret
```

Or pass them as flags on every command:

```bash
--api-key YOUR_KEY --api-secret YOUR_SECRET
```

---

## Logging

On first run, the bot automatically creates the `logs/` directory (if it does not exist) and writes structured logs to `logs/trading_bot.log`.

- **You do not need to create the `logs/` folder manually.**
- The log file rotates at **5 MB** and keeps **3 backups**.
- The `logs/` directory is excluded from version control via `.gitignore`.

---

## How to Run

All commands are run from the project root (`trading_bot/`).

### Market BUY order

```bash
python cli.py \
  --api-key $BINANCE_API_KEY --api-secret $BINANCE_API_SECRET \
  --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Limit SELL order

```bash
python cli.py \
  --api-key $BINANCE_API_KEY --api-secret $BINANCE_API_SECRET \
  --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000
```

### Stop-Market BUY order

```bash
python cli.py \
  --api-key $BINANCE_API_KEY --api-secret $BINANCE_API_SECRET \
  --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --price 66000
```

### Verbose debug logging

```bash
python cli.py --log-level DEBUG \
  --api-key $BINANCE_API_KEY --api-secret $BINANCE_API_SECRET \
  --symbol ETHUSDT --side BUY --type MARKET --quantity 0.01
```

### Reduce-only flag (close a position)

```bash
python cli.py \
  --api-key $BINANCE_API_KEY --api-secret $BINANCE_API_SECRET \
  --symbol BTCUSDT --side SELL --type MARKET --quantity 0.001 --reduce-only
```

---

## CLI Reference

| Argument | Required | Description |
|---|---|---|
| `--api-key` | Yes* | Binance API key (`BINANCE_API_KEY` env var) |
| `--api-secret` | Yes* | Binance API secret (`BINANCE_API_SECRET` env var) |
| `--symbol` | Yes | Trading pair, e.g. `BTCUSDT` |
| `--side` | Yes | `BUY` or `SELL` |
| `--type` | Yes | `MARKET`, `LIMIT`, or `STOP_MARKET` |
| `--quantity` | Yes | Contract quantity (positive number) |
| `--price` | Conditional | Required for `LIMIT` and `STOP_MARKET` orders |
| `--reduce-only` | No | Set `reduceOnly` flag on the order |
| `--log-level` | No | `DEBUG` / `INFO` / `WARNING` / `ERROR` (default: `INFO`) |

*Can also be set via environment variables.

---

## Example Output

```
┌─────────────────────────────────────────┐
│           ORDER REQUEST           │
└─────────────────────────────────────────┘
Symbol    : BTCUSDT
Side      : BUY
Type      : MARKET
Quantity  : 0.001
┌─────────────────────────────────────────┐
│           ORDER RESPONSE          │
└─────────────────────────────────────────┘
Order ID        : 3221685119
Client OID      : bot_market_001
Symbol          : BTCUSDT
Side            : BUY
Type            : MARKET
Status          : FILLED
Quantity        : 0.001
Executed Qty    : 0.001
Avg Price       : 67845.20
Price           : 0
Time in Force   : GTC
Update Time     : 1711540480000
✓ Order placed SUCCESSFULLY
```

---

## Assumptions

- Testnet base URL: `https://testnet.binancefuture.com`
- All orders use **USDT-M perpetual futures**
- `timeInForce` defaults to `GTC` for LIMIT orders
- No position-side (`HEDGE` mode) support — assumes **One-Way mode** (default on testnet)
- Quantity precision is not auto-adjusted; use the correct step size for each symbol
- The `logs/` directory is **not committed** to the repo; it is created automatically on first run
- - **Note:** Binance Futures Testnet (`testnet.binancefuture.com`) was deprecated in late 2025. The bot is fully functional and targets the correct testnet base URL — orders can be verified once Binance restores the service or via the `--dry-run` mode.

---

## License

MIT
