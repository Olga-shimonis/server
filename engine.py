import config
import time
import numpy as np
import asyncio
import statistics

file_ttft = 'ttft 30.txt'
file_tt= 'total time 30.txt'
file_throughput = 'throughput 30.txt'



ttft_stats = []


class requests:
    def __init__(self,id, img, input_tokens, gen_tokens, time):
        self.id = id
        self.time = time
        self.img = img
        self.input_tokens = input_tokens
        self.gen_tokens = gen_tokens
        self.start_preproc = None
        self.end_preproc = None
        self.start_gen = None
        self.end_gen = None





q =  asyncio.Queue()

async def arrival_process(rs, intervals):



    while len(rs) > 0:
        interval = intervals[0]
        await asyncio.sleep(interval)
        start_time = time.perf_counter()
        rs[0].start_preproc = start_time
        intervals.pop(0)

        await q.put(rs[0])
        rs.pop(0)





async def prefill_stage(batch_proc, batch_memory, evict=False):
    input_tok = []
    for reqs in batch_proc:
        batch_memory += reqs.input_tokens * config.Y_MEMORY_CONTEXT_TOKEN
        input_tok.append(reqs.input_tokens)
    evicted_before_prefill = []

    if batch_memory > config.M_acc:

        sorted_pairs = sorted(zip(input_tok, np.arange(len(input_tok)), batch_proc))
        input_tok, _, batch_proc = zip(*sorted_pairs)

        input_tok = list(input_tok)

        batch_proc = list(batch_proc)
        while batch_memory > config.M_acc:
            evicted_before_prefill.append(batch_proc[-1])
            batch_proc = batch_proc[:-1]
            batch_memory -= input_tok[-1] * config.Y_MEMORY_CONTEXT_TOKEN
            input_tok = input_tok[:-1]
    t = np.sqrt(sum(input_tok)) * config.B_COST_CONTEXT_TOKEN


    await asyncio.sleep(t)
    end_time = time.perf_counter()
    for req in batch_proc:
        req.end_preproc = end_time
        d = req.end_preproc - req.start_preproc
        ttft_stats.append(d)

        with open(file_ttft, 'a', encoding='utf-8') as file:
            file.write(str(d) + '\n')
    print(f'Stat: requests {len(ttft_stats)}, mean {statistics.mean(ttft_stats)}, mode {statistics.mode(ttft_stats)}, max {max(ttft_stats)}, min {min(ttft_stats)}')


    return evicted_before_prefill, batch_memory, batch_proc


async def decode_stage(batch_proc, batch_memory, finished, evict=False):
        output_tok = []
        for reqs in batch_proc:
            batch_memory += reqs.gen_tokens * config.Z_MEMORY_GEN_TOKEN
            output_tok.append(reqs.input_tokens)

        evicted_before_generation = []

        if batch_memory > config.M_acc:
            sorted_pairs = sorted(zip(output_tok, np.arange(len(output_tok)), batch_proc))
            output_tok, _,  batch_proc = zip(*sorted_pairs)

            output_tok = list(output_tok)
            batch_proc = list(batch_proc)
            while batch_memory > config.M_acc:
                evicted_before_generation.append(batch_proc[-1])
                batch_proc = batch_proc[:-1]
                batch_memory -= output_tok[-1] * config.Y_MEMORY_CONTEXT_TOKEN
                output_tok = output_tok[:-1]




        finished += len(output_tok)
        t = np.sqrt(sum(output_tok)) * config.C_COST_GEN_TOKENS
        start_gen_time = time.perf_counter()
        for req in batch_proc:
            req.start_gen = start_gen_time

        await asyncio.sleep(t)
        end_gen_time = time.perf_counter()
        for req in batch_proc:
            req.end_gen = end_gen_time
            d = req.end_gen - req.start_preproc
            #total_time_stats.append(d)
            with open(file_tt, 'a', encoding='utf-8') as file:
                file.write(str(d) + '\n')

        return evicted_before_generation, finished


class Accelerations:
    def __init__(self, id, batch):
        self.id = id
        self.batch = batch
        self.memory = 0



async def run_acceleration(acc, batch_queue):
    while True:
        acc.batch = await batch_queue.get()

        img_sum = 0
        for req in acc.batch:
            img_sum += req.img
        acc.memory += img_sum * config.X_MEMORY_IMG
        #print('Queue time', time.perf_counter() - acc.batch[0].start_preproc, acc.batch[0].id)
        await asyncio.sleep(img_sum * np.sqrt(len(acc.batch)) * config.A_COST_IMG)

        batch_size = len(acc.batch)
        finished = 0
        with open(file_throughput, 'a', encoding='utf-8') as file:
            file.write(str(batch_size) + '\n')

        evicted_before_prefill, acc.memory, acc.batch = await prefill_stage(acc.batch, acc.memory)

        evicted_before_generation, finished = await decode_stage(acc.batch, acc.memory, finished)
        acc.batch = []
        acc.memory = 0


        while finished != batch_size:
            if len(evicted_before_prefill) != 0:
                evicted_before_prefill, acc.memory, acc.batch = prefill_stage(evicted_before_prefill, acc.memory,
                                                                                 evict=True)
            new_batch = np.append(acc.batch, evicted_before_generation)
            evicted_before_generation, finished = decode_stage(new_batch, acc.memory, finished, evict=True)
            acc.memory = 0

        batch_queue.task_done()









async def scheduler(batch_queue):
    batch_memory = 0
    batch_proc = []
    img_sum = 0


    # last_action = asyncio.get_event_loop().time()
    # now = asyncio.get_event_loop().time()
    while True:

        now = time.perf_counter()
        if len(batch_proc) == 0:
            first_arrive = now
        else:
            first_arrive = batch_proc[0].start_preproc



        while len(batch_proc) < config.K*2 and not q.empty() and (now - first_arrive < 3 or len(batch_proc) == 0):
            req = await q.get()
            new_memory_batch = req.img * config.X_MEMORY_IMG

            if new_memory_batch + batch_memory < config.M_acc:
                batch_proc.append(req)
                img_sum += req.img

                batch_memory += new_memory_batch

            #now = asyncio.get_event_loop().time()
            if len(batch_proc) > 0:
                first_arrive = batch_proc[0].start_preproc

                now = time.perf_counter()
                if now - first_arrive > 3 and len(batch_proc) > 1:
                    break


        if len(batch_proc) == 0:
            await asyncio.sleep(0.01)
            continue

        print(batch_proc[0].time, batch_proc[-1].time)






        batch_proc.sort(key=lambda req: (-req.img))

        batch_size = len(batch_proc)
        b_1, b_2, b_3, b_4 = [], [], [], []

        if batch_size >= 10:

            b_1 = batch_proc.copy()[:len(batch_proc)//10]
            b_2 = batch_proc.copy()[len(batch_proc)//10:len(batch_proc)//4]
            b_3 = batch_proc.copy()[len(batch_proc) // 4:len(batch_proc) // 2]
            b_4 = batch_proc.copy()[len(batch_proc) // 2:]

        elif batch_size >= 6:

            b_1 = batch_proc.copy()[:len(batch_proc) // 4]
            b_2 = batch_proc.copy()[len(batch_proc) // 4:len(batch_proc) // 2]
            b_3 = batch_proc.copy()[len(batch_proc) // 2:]


        elif batch_size >= 4:
            b_1 = batch_proc.copy()[:len(batch_proc) // 2]
            b_2 = batch_proc.copy()[len(batch_proc) // 2:]

        else:
            b_1 = batch_proc.copy()




        if len(b_1) > 0:
            await batch_queue.put(b_1)
        if len(b_2) > 0:
            await batch_queue.put(b_2)
        if len(b_3) > 0:
            await batch_queue.put(b_3)
        if len(b_4) > 0:
            await batch_queue.put(b_4)






        batch_memory = 0
        batch_proc = []
        img_sum = 0