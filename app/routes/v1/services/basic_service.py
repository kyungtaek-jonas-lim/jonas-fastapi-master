import asyncio
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import time


# =========================================================
# ASYNC
# =========================================================
# Task Status
class TaskStatus(Enum):
    ACCEPTED = "ACCEPTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILURE = "FAILURE"

# Task Storage
tasks_status = {}

# Common
async def long_running_back(task_id: str):
    tasks_status[task_id] = TaskStatus.IN_PROGRESS
    await asyncio.sleep(10)
    tasks_status[task_id] = TaskStatus.COMPLETED

# Queue Thread
executor = ThreadPoolExecutor(max_workers=4)
def cpu_bound_task(task_id: str):
    tasks_status[task_id] = TaskStatus.IN_PROGRESS
    time.sleep(10)
    tasks_status[task_id] = TaskStatus.COMPLETED