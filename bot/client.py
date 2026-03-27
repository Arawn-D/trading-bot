"""Binance Futures Testnet REST client."""

from __future__ import annotations

import hashlib
import hmac
import time
import urllib.parse
from typing import Any

import requests

from bot.logging_config import setup_logging

TESTNET_BASE_URL = "https://testnet.binancefuture.com"

logger = setup_logging()


class BinanceAPIError(Exception):
    """Raised when the Binance API returns an error response."""

    def __init__(self, code: int, msg: str) -> None:
        self.code = code
        self.msg = msg
        super().__init__(f"Binance API error {code}: {msg}")


class BinanceClient:
    """Thin wrapper around the Binance Futures Testnet REST API."""

    def __init__(self, api_key: str, api_secret: str, base_url: str = TESTNET_BASE_URL) -> None:
        if not api_key or not api_secret:
            raise ValueError("api_key and api_secret must not be empty.")
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({"X-MBX-APIKEY": self.api_key})

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _sign(self, params: dict) -> dict:
        """Append timestamp and HMAC-SHA256 signature."""
        params["timestamp"] = int(time.time() * 1000)
        query = urllib.parse.urlencode(params)
        signature = hmac.new(
            self.api_secret.encode(), query.encode(), hashlib.sha256
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(
        self,
        method: str,
        path: str,
        params: dict | None = None,
        signed: bool = False,
    ) -> Any:
        url = f"{self.base_url}{path}"
        params = params or {}

        if signed:
            params = self._sign(params)

        logger.debug("REQUEST  %s %s params=%s", method.upper(), path, params)

        try:
            resp = self._session.request(
                method,
                url,
                params=params if method.upper() == "GET" else None,
                data=params if method.upper() == "POST" else None,
                timeout=10,
            )
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network failure: %s", exc)
            raise ConnectionError(f"Cannot reach {self.base_url}: {exc}") from exc
        except requests.exceptions.Timeout as exc:
            logger.error("Request timed out: %s", exc)
            raise TimeoutError(f"Request to {url} timed out.") from exc

        logger.debug("RESPONSE %s %s body=%s", resp.status_code, path, resp.text[:500])

        try:
            body = resp.json()
        except ValueError:
            logger.error("Non-JSON response (status %s): %s", resp.status_code, resp.text)
            resp.raise_for_status()
            raise

        if isinstance(body, dict) and "code" in body and body["code"] != 200:
            raise BinanceAPIError(body["code"], body.get("msg", "Unknown error"))

        return body

    # ------------------------------------------------------------------ #
    # Public API methods                                                   #
    # ------------------------------------------------------------------ #

    def get_exchange_info(self) -> dict:
        """Fetch exchange metadata (symbol info, filters)."""
        return self._request("GET", "/fapi/v1/exchangeInfo")

    def get_account(self) -> dict:
        """Fetch futures account details."""
        return self._request("GET", "/fapi/v2/account", signed=True)

    def new_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float | None = None,
        time_in_force: str = "GTC",
        reduce_only: bool = False,
    ) -> dict:
        """
        Place a new futures order.

        Parameters
        ----------
        symbol      : e.g. "BTCUSDT"
        side        : "BUY" | "SELL"
        order_type  : "MARKET" | "LIMIT" | "STOP_MARKET"
        quantity    : contract quantity
        price       : required for LIMIT / STOP_MARKET
        time_in_force: "GTC" | "IOC" | "FOK"  (ignored for MARKET)
        reduce_only : whether to set reduceOnly flag
        """
        params: dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            if price is None:
                raise ValueError("price is required for LIMIT orders.")
            params["price"] = price
            params["timeInForce"] = time_in_force

        elif order_type == "STOP_MARKET":
            if price is None:
                raise ValueError("stopPrice is required for STOP_MARKET orders.")
            params["stopPrice"] = price

        if reduce_only:
            params["reduceOnly"] = "true"

        logger.info(
            "Placing %s %s order | symbol=%s qty=%s price=%s",
            side,
            order_type,
            symbol,
            quantity,
            price,
        )

        result = self._request("POST", "/fapi/v1/order", params=params, signed=True)
        logger.info("Order placed successfully | orderId=%s status=%s", result.get("orderId"), result.get("status"))
        return result
