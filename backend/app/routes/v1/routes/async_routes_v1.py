import asyncio
import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException
from ..services.async_service import AsyncType, TaskStatus, tasks_status, io_bound_task, executor, cpu_bound_task

router = APIRouter()

# =========================================================
# ASYNC Result
# =========================================================

# Async Request
@router.get("/result/{task_id}")
async def async_result(task_id: str):

    # get status
    status = tasks_status.get(task_id)
    if not status:
        raise HTTPException(status_code=400, detail="Not Found")

    # response
    result = {
        "task_id": task_id,
        "status": status.value
    }
    if status == TaskStatus.COMPLETED:
        tasks_status.pop(task_id, None)
    return result


# =========================================================
# ASYNC (I/O-bound)
# =========================================================

# Async Request
@router.post("/io-bound")
async def async_io_bound_request(background_tasks: BackgroundTasks):
    return async_logic_example(async_type= AsyncType.IO_BOUND, background_tasks=background_tasks)


# =========================================================
# ASYNC (CPU-bound) (Queue Thread)
# =========================================================

# Async Request
@router.post("/cpu-bound")
async def async_cpu_bound_request():
    return async_logic_example(async_type= AsyncType.CPU_BOUND)


# =========================================================
# Functions
# =========================================================
def async_logic_example(async_type: AsyncType, background_tasks: BackgroundTasks=None):
    # generate ID (UUIDv4)
    task_id = str(uuid.uuid4())
    limit_cnt = 3
    cnt = 1
    while tasks_status.get(task_id):
        task_id = str(uuid.uuid4())
        if cnt >= limit_cnt:
            raise HTTPException(status_code=500, detail="Internal Server Error")
        cnt += 1

    # async biz logic
    if async_type == AsyncType.IO_BOUND:
        if not background_tasks:
            raise HTTPException(status_code=500, detail="Internal Server Error")
        background_tasks.add_task(io_bound_task, task_id)
    elif async_type == AsyncType.CPU_BOUND:
        loop = asyncio.get_running_loop()
        loop.run_in_executor(executor, cpu_bound_task, task_id)
    else:
        raise HTTPException(status_code=500, detail="Internal Server Error")

    # response
    result = {
        "task_id": task_id,
        "status": TaskStatus.ACCEPTED.value
    }
    return result