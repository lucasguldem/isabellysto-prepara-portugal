from __future__ import annotations

import argparse
import json
import os
from urllib import parse, request

from pbi_preflight import collect_missing_env_vars


def build_refresh_request(env: dict[str, str]) -> dict[str, object]:
    workspace_id = env["PBI_WORKSPACE_ID"]
    dataset_id = env["PBI_DATASET_ID"]
    refresh_url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/refreshes"
    payload = {"notifyOption": env.get("PBI_REFRESH_NOTIFY_OPTION", "MailOnFailure")}
    return {"url": refresh_url, "payload": payload}


def _fetch_access_token(env: dict[str, str]) -> str:
    token_url = f"https://login.microsoftonline.com/{env['PBI_TENANT_ID']}/oauth2/v2.0/token"
    payload = parse.urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": env["PBI_CLIENT_ID"],
            "client_secret": env["PBI_CLIENT_SECRET"],
            "scope": "https://analysis.windows.net/powerbi/api/.default",
        }
    ).encode("utf-8")
    token_request = request.Request(token_url, data=payload, method="POST")
    with request.urlopen(token_request) as response:
        body = json.loads(response.read().decode("utf-8"))
    return body["access_token"]


def trigger_refresh(env: dict[str, str]) -> dict[str, object]:
    access_token = _fetch_access_token(env)
    refresh_request = build_refresh_request(env)
    req = request.Request(
        refresh_request["url"],
        data=json.dumps(refresh_request["payload"]).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with request.urlopen(req) as response:
        return {
            "status": response.status,
            "url": refresh_request["url"],
            "payload": refresh_request["payload"],
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Trigger a Power BI dataset refresh.")
    parser.add_argument("--dry-run", action="store_true", help="Print the intended refresh request and exit.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    env = dict(os.environ)
    missing = collect_missing_env_vars(env)

    if args.dry_run:
        preview = {
            "missing_env_vars": missing,
            "request": (
                build_refresh_request(env)
                if not missing or {"PBI_WORKSPACE_ID", "PBI_DATASET_ID"}.isdisjoint(missing)
                else None
            ),
        }
        print(json.dumps(preview, indent=2, ensure_ascii=False))
        return 0

    if missing:
        print(json.dumps({"missing_env_vars": missing}, indent=2, ensure_ascii=False))
        return 1

    response = trigger_refresh(env)
    print(json.dumps(response, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
