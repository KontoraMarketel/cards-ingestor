import asyncio
import logging

import aiohttp

GET_ALL_CARDS = "https://content-api.wildberries.ru/content/v2/get/cards/list"


async def fetch_data(api_token: str) -> list:
    headers = {
        "Authorization": api_token
    }
    limit = 100
    cursor = None
    all_cards = []

    async with aiohttp.ClientSession(headers=headers) as session:
        while True:
            payload = {
                "settings": {
                    "cursor": {"limit": limit},
                    "filter": {"withPhoto": -1}
                }
            }

            if cursor:
                payload["settings"]["cursor"].update(cursor)

            data = await fetch_page_with_retry(session, GET_ALL_CARDS, payload)

            cards = data.get("cards", [])
            cursor_data = data.get("cursor", {})
            total = cursor_data.get("total", 0)

            all_cards.extend(cards)

            if total == 0:
                break

            cursor = {
                "updatedAt": cursor_data.get("updatedAt"),
                "nmID": cursor_data.get("nmID")
            }

    return all_cards


async def fetch_page_with_retry(session, url, payload):
    while True:
        async with session.post(url, json=payload) as response:
            if response.status == 429:
                retry_after = int(response.headers.get('X-Ratelimit-Retry', 10))
                logging.warning(f"Rate limited (429). Retrying after {retry_after} seconds...")
                await asyncio.sleep(retry_after)
                continue

            response.raise_for_status()
            return await response.json()
