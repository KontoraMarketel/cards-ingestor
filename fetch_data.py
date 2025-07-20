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

            async with session.post(GET_ALL_CARDS, json=payload) as response:
                data = await response.json()
                if response.status != 200:
                    logging.error(f"Error fetching cards: {response.status}, {data}")
                    response.raise_for_status()

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
