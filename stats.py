import pandas as pd
import matplotlib.pyplot as plt
import statistics


ttft_db_20 = pd.read_csv('ttft 20.txt', header=None)
total_time_20 = pd.read_csv('total time 20.txt', header=None)
through_20 = pd.read_csv('throughput_20.txt', header=None)


ttft_db_15 = pd.read_csv('ttft 15.txt', header=None)
total_time_15 = pd.read_csv('total time 15.txt', header=None)
through_15 = pd.read_csv('throughput_15.txt', header=None)





print(f'N = 15 mean TTFT = {ttft_db_15[0].mean()}, mode TTFT = {statistics.mode(list(ttft_db_15[0]))}, max TTFT = {ttft_db_15[0].max()}, min TTFT = {ttft_db_15[0].min()}')
print(f'N = 15 mean T = {total_time_15[0].mean()}, mode T = {statistics.mode(list(total_time_15[0]))}, max T = {total_time_15[0].max()}, min T = {total_time_15[0].min()}')
print(f'N = 20 mean TTFT = {ttft_db_20[0].mean()}, mode TTFT = {statistics.mode(list(ttft_db_20[0]))}, max TTFT = {ttft_db_20[0].max()}, min TTFT = {ttft_db_20[0].min()}')
print(f'N = 20 mean T = {total_time_20[0].mean()}, mode T = {statistics.mode(list(total_time_20[0]))}, max T = {total_time_20[0].max()}, min T = {total_time_20[0].min()}')


plt.plot(ttft_db_20)
plt.xlabel('requests')
plt.ylabel('TTFT (s)')
plt.title('TTFT N = 20, 50000 requests')
plt.show()
plt.plot(total_time_20)
plt.xlabel('requests')
plt.ylabel('Total time (s)')
plt.title('Total time N = 20, 50000 requests')
plt.show()

plt.plot(ttft_db_15)
plt.xlabel('requests')
plt.ylabel('TTFT (s)')
plt.title('TTFT N = 15, 50000 requests')
plt.show()
plt.plot(total_time_15)
plt.xlabel('requests')
plt.ylabel('Total time (s)')
plt.title('Total time N = 15, 50000 requests')
plt.show()

