import asyncio
import json
import os.path
import aiohttp

URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=protein&db=nuccore&retmode=json&id="
DATA_DIR = "api_calls"
if not os.path.isdir(DATA_DIR):
    raise ValueError(f"DATA_DIR {DATA_DIR} does not exist!!!")


async def make_request(session, seq_id):
    text = ""
    ids = []
    url = f"{URL}{seq_id}"
    status = 200
    try:
        async with session.get(url) as resp:
            status = resp.status
            text = await resp.text()
            try:
                if status == 200:
                    data = json.loads(text)
                    linksets = data["linksets"]
                    for link in linksets:
                        dbs = link.get("linksetdbs")
                        if dbs is not None:
                            for db in dbs:
                                if db["linkname"] == "protein_nuccore":
                                    ids = db["links"]
            except:  # This is super lazy
                if status == 200:
                    status = 400

    except:  # This is super lazy
        if status == 200:
            status = 400
    return seq_id, status, text, ids


async def make_calls(seq_ids, retry_num=0):

    if retry_num == 10:
        print("Did 10 retries")
        with open(f"{DATA_DIR}/inconclusive.txt", "w") as f:
            f.write(seq_ids)
        return

    # connector = aiohttp.TCPConnector(limit=10)
    connector = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for seq_id in seq_ids:
            tasks.append(asyncio.ensure_future(make_request(session, seq_id)))
            await asyncio.sleep(0.1001)  # a wait a little more than a tenth of a second for good luck

        results = await asyncio.gather(*tasks)

        ids_to_retry = []
        with open(f"{DATA_DIR}/have_id{retry_num}.txt", "w") as good_f, open(
            f"{DATA_DIR}/no_id{retry_num}.txt", "w"
        ) as bad_f:
            for result in results:
                seq_id, status, text, ids = result
                if not status == 200:
                    ids_to_retry.append(seq_id)
                elif ids:
                    good_f.write(f"{seq_id}:{','.join(ids)}\n")
                else:
                    bad_f.write(f"{seq_id}\n")

    if ids_to_retry:
        retry_num += 1
        print(f"Retry num: {retry_num}")
        await make_calls(ids_to_retry, retry_num)
    return


async def main():
    seq_ids = []
    with open("delete.txt", "r") as f:
        for line in f:
            seq_ids.append(line.strip())

    # seq_ids = ["WP_011508594.1", "WP_011522341.1", "WP_012447589.1"]
    await make_calls(seq_ids)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
