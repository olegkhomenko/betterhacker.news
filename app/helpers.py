import aiohttp
import asyncio

BATCH_SIZE = 15


async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.json()


async def process_batch(session, urls):
    tasks = []
    for url in urls:
        task = asyncio.ensure_future(fetch_url(session, url))
        tasks.append(task)
    return await asyncio.gather(*tasks)


async def process_urls(urls, batch_size=BATCH_SIZE):
    async with aiohttp.ClientSession() as session:
        batches = [urls[i : i + batch_size] for i in range(0, len(urls), batch_size)]
        results = []
        for batch in batches:
            batch_results = await process_batch(session, batch)
            results.extend(batch_results)
        return results
