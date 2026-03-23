import config
import engine
import asyncio
import pandas as pd
from datetime import datetime


requests_db = pd.read_csv('AzureLMMInferenceTrace_multimodal.csv')
requests_db = requests_db.iloc[:50000]

requests_db['time'] = requests_db['TIMESTAMP'].apply(lambda x: x.split('T')[1])
requests_db['time'] = requests_db['time'].apply(lambda x: x[:-1])
print(requests_db)

rs = []
k = 0
for row in requests_db.itertuples():
    rs.append(engine.requests(k, row[2], row[3], row[4], datetime.strptime(str(row[5]), '%H:%M:%S.%f')))
    k += 1

intervals = [0]
for i in range(1, len(rs)):
    time_1 = rs[i-1].time
    time_2 = rs[i].time
    intervals.append((time_2-time_1).seconds)




async def main():
    gpu = []
    for i in range(config.N_acc):
        gpu.append(engine.Accelerations(i, []))


    batch_queue = asyncio.Queue()

    for i in gpu:
        asyncio.create_task(engine.run_acceleration(i, batch_queue))




    await asyncio.gather(
        engine.arrival_process(rs, intervals),
        engine.scheduler(batch_queue),
    )

    await batch_queue.join()




if __name__ == "__main__":

    asyncio.run(main())