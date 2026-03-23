# Server simulation

## Description 

Server gets requests from file `AzureLMMInferenceTrace_multimodal.csv` and creates objects of class requests with attributes:

* `id` - request id (equivalent to the order of arrival)
* `time` - time of arrival (from column `TIMESTAMP`)
* `img` - number of images (from column `NumImages`)
* `input_tokens` -  number of context tokens (from column `ContexTokens`)
* `gen_tokens` - number of generated tokens from column `GeneratedTokens`)
* `start_preproc` - relative time of arrival at the server
* `end_preproc` - relative time of ending of Preprocessing 
* `start_gen` -  relative time of beginning of generation
* `end_gen` -  relative time of ending of generation

The function `scheduler` distributes requests into batches according to the following principle:

1) The batch is formed until no more than 3 seconds have passed since the earliest request appeared or the batch reaches the size of K*2.
2) Next, the batch is sorted in descending order of the number of images.
3) The resulting batch is divided into several batches (4, 3, 2, 1) depending on their size. The size of the resulting batches depends on the number of images (the more images, the fewer requests per batch).

   <pre>
        if batch_size >= 16:

            b_1 = batch_proc.copy()[:len(batch_proc)//10]
            b_2 = batch_proc.copy()[len(batch_proc)//10:len(batch_proc)//4]
            b_3 = batch_proc.copy()[len(batch_proc) // 4:len(batch_proc) // 2]
            b_4 = batch_proc.copy()[len(batch_proc) // 2:]

        elif batch_size >= 8:

            b_1 = batch_proc.copy()[:len(batch_proc) // 4]
            b_2 = batch_proc.copy()[len(batch_proc) // 4:len(batch_proc) // 2]
            b_3 = batch_proc.copy()[len(batch_proc) // 2:]


        elif batch_size >= 4:
            b_1 = batch_proc.copy()[:len(batch_proc) // 2]
            b_2 = batch_proc.copy()[len(batch_proc) // 2:]

        else:
            b_1 = batch_proc.copy()
   </pre>

Next, the batches go to free accelerators. Class `Accelerator` has attributes:

* `id`
* `batch` - list of requests that the accelerator processes
* `memory` - amount of memory occupied

Each accelerator first processes images, then context tokens, and generates output tokens.

If the accelerator runs out of memory during the processing or generation stage, the requests in the batch are sorted by increasing memory footprint. The last requests in the batch are evicted until the batch fits in memory. Then the remaining requests are processed or generated, after which the evicted requests are loaded back into memory, and processing continues.



## Test configuration:

<pre>
A_COST_IMG = 0.008
B_COST_CONTEXT_TOKEN = 5e-5
C_COST_GEN_TOKENS = 0.005
X_MEMORY_IMG = 6000
Y_MEMORY_CONTEXT_TOKEN = 40
Z_MEMORY_GEN_TOKEN = 40
M_acc = 2e7
K = 15

</pre>

## Results
Time to first token for first 10000 requests

| N | Mean | Median | Max | Min |
| :--- | :---: | :---: | :---:  | :---: |
| 15 | 1096.9240951536267 | 1098.8678830000572 | 2165.0263961999444 | 0.0686583999777212 |
| 20 | 540.7039546100111 | 527.9426424000412 | 995.116417299956 | 0.0460666000144556 |
| 25 | 191.54983671691943 | 201.25675229995977 | 319.5452687999932 | 0.030958899995312 |
| 30 | 50.08267596248783 | 17.98727740009781 | 213.0327885999577 | 0.0148264999734237 |

Total time for first 10000 requests


| N | Mean | Median | Max | Min |
| :--- | :---: | :---: | :---:  | :---: |
| 15 | 1120.813653590948 | 1118.263390999986 | 2438.588019100018 | 3.9322435000212863 |
| 20 | 564.4269609147907 | 546.2880118000321 | 1436.922390999971 | 1.863719799905084 |
| 25 | 215.29441930075978 | 222.81302970007528 | 833.4084855000256 | 1.865089499973692 |
| 30 | 73.83259591907283 | 43.99259630008601 | 660.5752685000189 |  0.18764130002819 |



<img width="1609" height="842" alt="image" src="https://github.com/user-attachments/assets/08f1c103-3662-4be6-9dec-cbdfdb215a98" />

<img width="1639" height="839" alt="image" src="https://github.com/user-attachments/assets/711a15ac-afd9-48fa-af0b-47ace790a0de" />

Obviously, the best option is with N = 30

## Possible options for improvement

To reduce latency we can implement:

* To divide requests into batches we can distribute the number of images and tokens more evenly.
* Estimate the approximate batch processing and generation time and delete or add requests to the batch based on time constraints.
* Implement continuous batching

