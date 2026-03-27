"""High-level order placement logic."""

from __future__ import annotations

from typing import Any

from bot.client import BinanceClient, BinanceAPIError
from bot.logging_config import setup_logging

logger = setup_logging()


def _format_order_response(resp: dict) -> str:
    """Return a human-readable summary of an order response."""
    lines = [
        "",
        "┌─────────────────────────────────────────┐",
        "│           ORDER RESPONSE                │",
        "└─────────────────────────────────────────┘",
        f"  Order ID      : {resp.get('orderId', 'N/A')}",
        f"  Client OID    : {resp.get('clientOrderId', 'N/A')}",
        f"  Symbol        : {resp.get('symbol', 'N/A')}",
        f"  Side          : {resp.get('side', 'N/A')}",
        f"  Type          : {resp.get('type', 'N/A')}",
        f"  Status        : {resp.get('status', 'N/A')}",
        f"  Quantity      : {resp.get('origQty', 'N/A')}",
        f"  Executed Qty  : {resp.get('executedQty', 'N/A')}",
        f"  Avg Price     : {resp.get('avgPrice', 'N/A')}",
        f"  Price         : {resp.get('price', 'N/A')}",
        f"  Time in Force : {resp.get('timeInForce', 'N/A')}",
        f"  Update Time   : {resp.get('updateTime', 'N/A')}",
    ]
    return "\n".join(lines)


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None = None,
    reduce_only: bool = False,
) -> dict[str, Any]:
    """
    Place an order and return the API response dict.

    Raises
    ------
    BinanceAPIError   : on API-level errors
    ConnectionError   : on network failures
    TimeoutError      : on request timeout
    """
    # Print order request summary
    print("\n┌─────────────────────────────────────────┐")
    print("│           ORDER REQUEST                 │")
    print("└─────────────────────────────────────────┘")
    print(f"  Symbol        : {symbol}")
    print(f"  Side          : {side}")
    print(f"  Type          : {order_type}")
    print(f"  Quantity      : {quantity}")
    if price is not None:
        print(f"  Price         : {price}")
    if reduce_only:
        print(f"  Reduce Only   : {reduce_only}")

    logger.info(
        "Submitting order | symbol=%s side=%s type=%s qty=%s price=%s",
        symbol, side, order_type, quantity, price,
    )

    try:
        resp = client.new_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            reduce_only=reduce_only,
        )
    except BinanceAPIError as exc:
        logger.error("API error placing order: %s", exc)
        print(f"\n✗ Order FAILED — Binance API error {exc.code}: {exc.msg}")
        raise
    except (ConnectionError, TimeoutError) as exc:
        logger.error("Network error placing order: %s", exc)
        print(f"\n✗ Order FAILED — Network error: {exc}")
        raise

    print(_format_order_response(resp))
    print("\n✓ Order placed SUCCESSFULLY\n")
    return resp
