#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
import time
import warnings
from pathlib import Path
from typing import Any, Dict, Mapping, Optional
from urllib.parse import urlsplit

warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL.*")

import requests

try:
    from urllib3.exceptions import NotOpenSSLWarning

    warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
except Exception:
    pass


DEFAULT_SIGNED = "/private/tmp/gopay_linkedapps_signed_latest.json"
DEFAULT_BASE_URL = "https://customer.gopayapi.com"
DEFAULT_HMAC_KEY = "4&G6DbV&j8QZs~{)(Ila_w_|v@aqJq]E-;*(J9PanZ8sm01kTi{X<iG``]d7P&L"
DEFAULT_X_E2 = "ED9A2B38749FBDE9ACA61D6A685B7"


def load_baseline(path: str) -> Dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    headers = data.get("headers")
    if not isinstance(headers, dict):
        raise ValueError(f"{path} does not contain a headers object")
    return data


def lower_headers(headers: Mapping[str, str]) -> Dict[str, str]:
    return {str(k).lower(): str(v) for k, v in headers.items()}


def bearer_token(authorization: str) -> str:
    prefix = "Bearer "
    return authorization[len(prefix) :] if authorization.startswith(prefix) else authorization


def request_body(args: argparse.Namespace) -> str:
    if args.body_file:
        return Path(args.body_file).read_text(encoding="utf-8")
    if args.body is not None:
        return args.body
    if args.json_body is not None:
        return json.dumps(json.loads(args.json_body), separators=(",", ":"), ensure_ascii=False)
    return ""


def split_target(base_url: str, target: str) -> tuple[str, str, str]:
    if target.startswith("http://") or target.startswith("https://"):
        parsed = urlsplit(target)
        path = parsed.path or "/"
        if parsed.query:
            path = f"{path}?{parsed.query}"
        return f"{parsed.scheme}://{parsed.netloc}", parsed.netloc, path

    parsed_base = urlsplit(base_url)
    if not parsed_base.scheme or not parsed_base.netloc:
        raise ValueError(f"invalid base url: {base_url}")
    path = target if target.startswith("/") else f"/{target}"
    return base_url.rstrip("/"), parsed_base.netloc, path


def canonical_message(
    headers: Mapping[str, str],
    *,
    method: str,
    host: str,
    path: str,
    body: str,
    nonce_hex: str,
    timestamp_ms: int,
) -> str:
    h = lower_headers(headers)
    body_md5 = hashlib.md5(body.encode("utf-8")).hexdigest()

    return (
        f"{h['x-apptype']};"
        f"{h['x-phonemodel']}:{bearer_token(h['authorization'])};"
        f"{h['x-uniqueid']}:{body};"
        f"{body_md5}:{host}{path};"
        f"{method.upper()}:{timestamp_ms};"
        f"{h['x-deviceos']}:{h['x-appversion']};"
        f"{h['x-m1']}:{h['x-appid']};"
        f"{nonce_hex}:{h['x-phonemake']};"
        f"{h['x-platform']}"
    )


def sign_x_e1(
    headers: Mapping[str, str],
    *,
    method: str,
    host: str,
    path: str,
    body: str = "",
    key: str = DEFAULT_HMAC_KEY,
    nonce_hex: Optional[str] = None,
    timestamp_ms: Optional[int] = None,
) -> tuple[str, str]:
    timestamp_ms = int(time.time() * 1000) if timestamp_ms is None else timestamp_ms
    nonce_hex = os.urandom(80).hex() if nonce_hex is None else nonce_hex.lower()
    if len(nonce_hex) != 160 or any(c not in "0123456789abcdef" for c in nonce_hex):
        raise ValueError("nonce must be exactly 160 lowercase hex chars")

    msg = canonical_message(
        headers,
        method=method,
        host=host,
        path=path,
        body=body,
        nonce_hex=nonce_hex,
        timestamp_ms=timestamp_ms,
    )
    digest = hmac.new(key.encode("utf-8"), msg.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{digest}:{nonce_hex}:D:{timestamp_ms}", msg


def signed_headers(
    baseline_headers: Mapping[str, str],
    *,
    method: str,
    host: str,
    path: str,
    body: str,
    key: str,
    print_canonical: bool,
) -> tuple[Dict[str, str], Optional[str]]:
    headers = {str(k): str(v) for k, v in baseline_headers.items()}
    headers["host"] = host
    headers["x-e2"] = headers.get("x-e2") or DEFAULT_X_E2
    xe1, msg = sign_x_e1(headers, method=method, host=host, path=path, body=body, key=key)
    headers["x-e1"] = xe1
    if body and "content-type" not in lower_headers(headers):
        headers["content-type"] = "application/json"
    return headers, msg if print_canonical else None


def send_request(args: argparse.Namespace, destructive_ok: bool) -> int:
    baseline = load_baseline(args.headers_json)
    method = args.method.upper()
    base_url, host, path = split_target(args.base_url, args.target)
    body = request_body(args)

    if method not in {"GET", "HEAD", "OPTIONS"} and not destructive_ok and not args.yes and not args.dry_run:
        raise SystemExit("Refusing to send a non-read request without --yes")

    headers, msg = signed_headers(
        baseline["headers"],
        method=method,
        host=host,
        path=path,
        body=body,
        key=args.key,
        print_canonical=args.print_canonical,
    )
    url = f"{base_url}{path}"

    if args.print_headers:
        safe_headers = dict(headers)
        if "authorization" in lower_headers(safe_headers):
            for k in list(safe_headers):
                if k.lower() == "authorization":
                    safe_headers[k] = safe_headers[k][:24] + "...<redacted>"
        print(json.dumps(safe_headers, indent=2, ensure_ascii=False))
    if msg is not None:
        print(msg)

    if args.dry_run:
        print(f"dry-run: {method} {url}")
        return 0

    data = body.encode("utf-8") if body or method not in {"GET", "HEAD"} else None
    resp = requests.request(method, url, headers=headers, data=data, timeout=args.timeout)
    print(f"status: {resp.status_code}")
    print(resp.text[: args.max_body])
    return 0 if resp.ok else 1


def linkedapps(args: argparse.Namespace) -> int:
    args.method = "GET"
    args.target = "/v1/linkedapps"
    args.body = None
    args.body_file = ""
    args.json_body = None
    return send_request(args, destructive_ok=True)


def unlink(args: argparse.Namespace) -> int:
    args.method = "PATCH"
    args.target = f"/v1/links/{args.link_id}"
    args.body = None
    args.body_file = ""
    args.json_body = None
    return send_request(args, destructive_ok=False)


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--headers-json", default=DEFAULT_SIGNED, help="baseline signed request JSON")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--key", default=DEFAULT_HMAC_KEY)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--max-body", type=int, default=4000)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--print-headers", action="store_true")
    parser.add_argument("--print-canonical", action="store_true")
    parser.add_argument("--yes", action="store_true", help="required for non-read requests")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pure Python GoPay x-e1 signer and request client")
    sub = parser.add_subparsers(dest="command", required=True)

    p_linked = sub.add_parser("linkedapps", help="GET /v1/linkedapps")
    add_common(p_linked)
    p_linked.set_defaults(func=linkedapps)

    p_req = sub.add_parser("request", help="send an arbitrary signed request")
    add_common(p_req)
    p_req.add_argument("--method", default="GET")
    p_req.add_argument("--body")
    p_req.add_argument("--body-file", default="")
    p_req.add_argument("--json-body")
    p_req.add_argument("target", help="path or full URL")
    p_req.set_defaults(func=lambda a: send_request(a, destructive_ok=False))

    p_unlink = sub.add_parser("unlink", help="PATCH /v1/links/{link_id}; requires --yes")
    add_common(p_unlink)
    p_unlink.add_argument("link_id")
    p_unlink.set_defaults(func=unlink)
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        return args.func(args)
    except requests.RequestException as exc:
        print(f"request error: {exc}", file=sys.stderr)
        return 2
    except (KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"signing error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
