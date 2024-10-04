import asyncio
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import time

'''
**CPU-bound Task**
- **Using a thread pool to process tasks**
- **Each thread consumes CPU resources to process tasks**
- **Executed synchronously for each thread (but can appear asynchronously from the overall service perspective)**

**I/O-bound asynchronous task**
- **The main thread handles all tasks (no worker threads created)**
- **While waiting for I/O operations, the event loop assigns asynchronous tasks to the main thread for processing**
- **CPU consumption is relatively low compared to a single thread**

**Speed Comparison**
- generally speaking, CPU-bound tasks, which consume more CPU resources and utilize multiple threads, are expected to be faster than I/O-bound tasks when considering speed alone.
'''


# =========================================================
# ASYNC
# =========================================================
# Async Type
class AsyncType(Enum):
    IO_BOUND = "IO_BOUND"
    CPU_BOUND = "CPU_BOUND"

# Task Status
class TaskStatus(Enum):
    ACCEPTED = "ACCEPTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

# Task Storage
tasks_status = {}

# Common
async def io_bound_task(task_id: str):
    tasks_status[task_id] = TaskStatus.IN_PROGRESS
    await asyncio.sleep(10)
    tasks_status[task_id] = TaskStatus.COMPLETED

# Queue Thread
executor = ThreadPoolExecutor(max_workers=4)
def cpu_bound_task(task_id: str):
    tasks_status[task_id] = TaskStatus.IN_PROGRESS
    time.sleep(10)
    tasks_status[task_id] = TaskStatus.COMPLETED