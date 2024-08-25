import logging

import httpx


async def load_notebook(
    host: str,
):
    logging.info("Loading notebook")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{host}/_marimo/")
        response.raise_for_status()
        logging.info(response.text)
        return
