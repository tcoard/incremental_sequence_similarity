import re
import asyncio
import os.path
from collections import defaultdict
import aiohttp

IN_FILE = "delete.txt"
MAX_RETRY = 10
PROCESS_AT_A_TIME = 20000
TIMEOUT_TIME = 120
API_PAUSE_TIME = 0.3334 # if using an API key this has to be >=0.1. If not using an API key, this has to be >=1/3
URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&report=genbank&conwithfeat=on&withparts=on&retmode=xml&id="

DATA_DIR = "api_calls"
if not os.path.isdir(DATA_DIR):
    raise ValueError(f"DATA_DIR {DATA_DIR} does not exist!!!")


def compliment(seq):
    """If the sequences is on the negative strand, get the compliment of the nucs and reverse the sequence"""
    comp = {"a": "t", "t": "a", "g": "c", "c": "g"}
    comp_seq = ""
    for nuc in seq:
        comp_seq += comp[nuc]
    return comp_seq[::-1]


def unchunk(chunk, still_chunked=None):
    """turn a chunk of data into lines + remaining chunked data"""
    # this could probably be a coroutine
    if still_chunked is not None:
        chunk = still_chunked + chunk
    lines = chunk.split(b"\n")
    still_chunked = lines.pop()
    return lines, still_chunked


async def get_data(session, prot_id, nuc_id):
    """Make the api request and parse the data
    Note: I chose not to use an XML parser because they can be slow with data this large
    """
    loc = ""
    looking_for_nuc_seq = True
    url = f"{URL}{nuc_id}"
    still_chunked = None
    try:
        async with session.get(url) as resp:

            status = resp.status
            # don't try to parse non 200 responses
            if status != 200:
                print(url)
                return prot_id, nuc_id, ""

            # the sequence line is too long, so we have to read it in in chunks
            async for chunk in resp.content.iter_chunked(1024):
                lines, still_chunked = unchunk(chunk, still_chunked)
                for line in lines:
                    line = line.decode().strip()

                    if line.startswith("<GBFeature_location>"):
                        temp_loc = re.search(">(.*)<", line).group(1)

                    elif line.startswith("<GBQualifier_value>"):
                        temp_prot_id = re.search(">(.*)<", line).group(1)
                        if temp_prot_id == prot_id:
                            loc = temp_loc
                            looking_for_nuc_seq = True

                    elif looking_for_nuc_seq and line.startswith("<GBSeq_sequence>"):
                        seq = re.search(">(.*)<", line).group(1)
                        start = 0
                        stop = 0
                        is_minus = False
                        if "complement" in loc:
                            search = re.search(r"complement\((\d+)..(\d+)\)", loc)
                            start = search.group(1)
                            stop = search.group(2)
                            is_minus = True
                        else:
                            start, stop = loc.split("..")

                        start = int(start)
                        stop = int(stop)
                        # get just the nucleotides from the location of our protein
                        seq = seq[start:stop]
                        if is_minus:
                            seq = compliment(seq)
                        return prot_id, nuc_id, seq

    except Exception as e:  # this is lazy, but any errors should end up here anyways
        print(e)
        return prot_id, nuc_id, ""


async def make_calls(seq_ids, retry_num=0):

    # if a sequence has 10+ ids and 10 have already failed, put that seq on the backburner
    if retry_num == MAX_RETRY:
        print("Did 10 retries")
        with open(f"{DATA_DIR}/inconclusive_nuc_seq.txt", "a") as f:
            f.write(str(seq_ids))
        return

    total_fail = []
    session_timeout = aiohttp.ClientTimeout(total=TIMEOUT_TIME)
    connector = aiohttp.TCPConnector()
    async with aiohttp.ClientSession(connector=connector, timeout=session_timeout) as session:
        tasks = []
        for prot_id in seq_ids:
            if len(seq_ids[prot_id]) == 0:
                total_fail.append(prot_id)
                continue
            # take it out of the list so that when we try it next, we try the next id
            # TODO if this script is used again, it might make sense to retry IDs that don't get a 200 response
            # right now we are not retrying IDs
            nuc_id = seq_ids[prot_id].pop(0)
            tasks.append(asyncio.ensure_future(get_data(session, prot_id, nuc_id)))
            await asyncio.sleep(API_PAUSE_TIME)  # a wait a little more than a tenth of a second for good luck

        results = await asyncio.gather(*tasks)

        ids_to_retry = {}
        with open(f"{DATA_DIR}/nuc_seqs{retry_num}.txt", "a") as good_f, open(
            f"{DATA_DIR}/failed{retry_num}.txt", "a"
        ) as bad_f:
            for result in results:
                prot_id, nuc_id, nuc_seq = result
                if nuc_seq == "":
                    ids_to_retry[prot_id] = seq_ids[prot_id]
                else:
                    good_f.write(f"{prot_id}:{nuc_id}:{nuc_seq}\n")

            for failed in total_fail:
                bad_f.write(f"{failed}\n")

    if ids_to_retry:
        retry_num += 1
        print(f"Retry num: {retry_num}")
        await make_calls(ids_to_retry, retry_num)
    return


async def main():
    total_finished = 0
    with open(IN_FILE, "r") as f:
        prot_id = ""
        seq_ids = defaultdict(list)
        for line in f:
            line = line.strip()
            if not line.startswith('"'):
                prot_id = line
            else:
                seq_ids[prot_id].append(line.strip('"'))

            # I am only running some at a time so that if it crashes, I still have some data
            # This will slow this down by a maximum of (TIMEOUT_TIME * total seq_ids / PROCESS_AT_A_TIME)
            if len(seq_ids) == PROCESS_AT_A_TIME:
                await make_calls(seq_ids)
                total_finished += PROCESS_AT_A_TIME
                print(f"finished: {total_finished}")
                seq_ids = defaultdict(list)

        await make_calls(seq_ids)
        total_finished += len(seq_ids)
        print(f"finished: {total_finished}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
