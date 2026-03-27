#!/usr/bin/env python3
"""
CLI entry point for the Binance Futures Testnet trading bot.

Usage examples
--------------
# Market BUY
python cli.py --api-key KEY --api-secret SECRET \
    --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# Limit SELL
python cli.py --api-key KEY --api-secret SECRET \
    --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 100000

# Stop-Market BUY
python cli.py --api-key KEY --api-secret SECRET \
    --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --price 70000

Credentials can also be supplied via environment variables:
  BINANCE_API_KEY, BINANCE_API_SECRET
"""

from __future__ import annotations

import argparse
import os
import sys

from bot.client import BinanceClient, BinanceAPIError
from bot.logging_config import setup_logging
from bot.orders import place_order
from bot.validators import ValidationError, validate_all

logger = setup_logging()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet trading bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Credentials (fall back to env vars)
    p.add_argument(
        "--api-key",
        default=os.getenv("BINANCE_API_KEY"),
        help="Binance API key (or set BINANCE_API_KEY env var)",
    )
    p.add_argument(
        "--api-secret",
        default=os.getenv("BINANCE_API_SECRET"),
        help="Binance API secret (or set BINANCE_API_SECRET env var)",
    )

    # Order parameters
    p.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    p.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL"],
        type=str.upper,
        help="Order side",
    )
    p.add_argument(
        "--type",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
        type=str.upper,
        help="Order type",
    )
    p.add_argument("--quantity", required=True, help="Contract quantity")
    p.add_argument(
        "--price",
        default=None,
        help="Limit price (required for LIMIT / STOP_MARKET)",
    )
    p.add_argument(
        "--reduce-only",
        action="store_true",
        default=False,
        help="Set reduceOnly flag on the order",
    )
    p.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: INFO)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Re-initialise logging at requested level
    setup_logging(args.log_level)

    # ── Credential check ──────────────────────────────────────────────
    if not args.api_key or not args.api_secret:
        parser.error(
            "API credentials are required. Pass --api-key / --api-secret or "
            "set BINANCE_API_KEY / BINANCE_API_SECRET environment variables."
        )

    # ── Input validation ──────────────────────────────────────────────
    try:
        params = validate_all(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
    except ValidationError as exc:
        logger.error("Validation failed: %s", exc)
        print(f"\n✗ Validation error: {exc}\n")
        return 1

    # ── Place order ───────────────────────────────────────────────────
    client = BinanceClient(api_key=args.api_key, api_secret=args.api_secret)

    try:
        place_order(
            client=client,
            symbol=params["symbol"],
            side=params["side"],
            order_type=params["order_type"],
            quantity=params["quantity"],
            price=params["price"],
            reduce_only=args.reduce_only,
        )
    except (BinanceAPIError, ConnectionError, TimeoutError, ValueError):
        # Already logged and printed inside place_order / client
        return 1
    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        print(f"\n✗ Unexpected error: {exc}\n")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
