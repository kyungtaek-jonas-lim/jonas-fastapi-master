from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from enum import Enum
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import time

class SchedulerType(Enum):
    ASYNC_IO = "ASYNC_IO" # Async I/O Bound
    BACKGROUND = "BACKGROUND" # Sync Background



# ===============================================================
# Scheduler
# ===============================================================

scheduler_async_io = AsyncIOScheduler()
executor = ThreadPoolExecutor(max_workers=4)
scheduler_background = BackgroundScheduler(executor=executor)



# ===============================================================
# Job Definition
# ===============================================================

# Job (Async)
async def my_job_async(type: str):
    print(f"[{type}] Job executed at {datetime.now()}")
    
    # # max_instances Test
    # time.sleep(10)
    # print(f"[{type}] Job finished at {datetime.now()}")

# Job (Sync)
def my_job_sync(type: str):
    print(f"[{type}] Job executed at {datetime.now()}")
    
    # # max_instances Test
    # time.sleep(10)
    # print(f"[{type}] Job finished at {datetime.now()}")



# ===============================================================
# Add Job to Schedulers
# ===============================================================

# Scheduler Setting Function (Async I/O)
def start_scheduler_async_io():
    type = SchedulerType.ASYNC_IO.value
    # scheduler.add_job(my_job, 'interval', seconds=10) # Every 10 seconds
    # scheduler.add_job(my_job, 'cron', second=10) # Every minute at 10 seconds
    scheduler_async_io.add_job(my_job_async, 'cron', second='0,10,20,30,40,50', args=[type], max_instances=1) # Every minute at 0,10,20,30,40,50 seconds
    # max_instance means the job will be created only one at a time (e.g. if the previous job is still running, the next job will be waiting in a queue and will be executed right after the previous one is done)
    scheduler_async_io.start()


# Scheduler Setting Function (Background)
def start_scheduler_background():
    type = SchedulerType.BACKGROUND.value
    scheduler_background.add_job(my_job_sync, 'cron', second='5,15,25,35,45,55', args=[type], max_instances=2) # Every minute at 0,10,20,30,40,50 seconds
    # The number of theeads is 4 so the job can be executed even if the previous job is not finished (max_instance=2)
    scheduler_background.start()


# Scheduler Shutdown Function
def shutdown_scheduler():
    scheduler_async_io.shutdown(wait=True) # wait: safe shutdown after all jobs running
    scheduler_background.shutdown(wait=True)