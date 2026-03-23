import pandas as pd
import matplotlib.pyplot as plt
import statistics


ttft_db_20 = pd.read_csv('metrics/ttft 20 new.txt', header=None)
total_time_20 = pd.read_csv('metrics/total time 20 new.txt', header=None)



ttft_db_15 = pd.read_csv('metrics/ttft 15 new.txt', header=None)
total_time_15 = pd.read_csv('metrics/total time 15 new.txt', header=None)

ttft_db_25 = pd.read_csv('metrics/ttft 25 new.txt', header=None)
total_time_25 = pd.read_csv('metrics/total time 25 new.txt', header=None)


ttft_db_30 = pd.read_csv('metrics/ttft 30 new.txt', header=None)
total_time_30 = pd.read_csv('metrics/total time 30 new.txt', header=None)

print(f'N = 15 mean TTFT = {ttft_db_15[0].mean()}, median TTFT = {ttft_db_15[0].median()}, max TTFT = {ttft_db_15[0].max()}, min TTFT = {ttft_db_15[0].min()}')
print(f'N = 15 mean T = {total_time_15[0].mean()}, median T = {total_time_15[0].median()}, max T = {total_time_15[0].max()}, min T = {total_time_15[0].min()}')
print(f'N = 20 mean TTFT = {ttft_db_20[0].mean()}, median TTFT = {ttft_db_20[0].median()}, max TTFT = {ttft_db_20[0].max()}, min TTFT = {ttft_db_20[0].min()}')
print(f'N = 20 mean T = {total_time_20[0].mean()}, median T = {total_time_20[0].median()}, max T = {total_time_20[0].max()}, min T = {total_time_20[0].min()}')
print(f'N = 25 mean TTFT = {ttft_db_25[0].mean()}, median TTFT = {ttft_db_25[0].median()}, max TTFT = {ttft_db_25[0].max()}, min TTFT = {ttft_db_25[0].min()}')
print(f'N = 25 mean T = {total_time_25[0].mean()}, median T = {total_time_25[0].median()}, max T = {total_time_25[0].max()}, min T = {total_time_25[0].min()}')
print(f'N = 30 mean TTFT = {ttft_db_30[0].mean()}, median TTFT = {ttft_db_30[0].median()}, max TTFT = {ttft_db_30[0].max()}, min TTFT = {ttft_db_30[0].min()}')
print(f'N = 30 mean T = {total_time_30[0].mean()}, median T = {total_time_30[0].median()}, max T = {total_time_30[0].max()}, min T = {total_time_30[0].min()}')


plt.plot(ttft_db_20, label='N=20')
plt.plot(ttft_db_25, label='N=25')
plt.plot(ttft_db_15, label='N=15')
plt.plot(ttft_db_30, label='N=30')
plt.legend()
plt.xlabel('requests')
plt.ylabel('TTFT (s)')
plt.title('TTFT 10000 requests')
plt.show()
plt.plot(total_time_20, label='N=20')
plt.plot(total_time_25, label='N=25')
plt.plot(total_time_15, label='N=15')
plt.plot(total_time_30, label='N=30')
plt.legend()
plt.xlabel('requests')
plt.ylabel('Total time (s)')
plt.title('Total time 10000 requests')
plt.show()


