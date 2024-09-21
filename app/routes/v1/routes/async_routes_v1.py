import asyncio
import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException
from ..services.async_service import TaskStatus, tasks_status, io_bound_task, executor, cpu_bound_task

router = APIRouter()

@router.get("")
def basic():
    return {"message": "succeeded in uploading!"}

# =========================================================
# ASYNC Result
# =========================================================

# Async Request
@router.get("/result/{task_id}")
def async_result(task_id: str):

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
@router.get("/io-bound")
async def async_io_bound_request(background_tasks: BackgroundTasks):

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
    background_tasks.add_task(io_bound_task, task_id)

    # response
    result = {
        "task_id": task_id,
        "status": TaskStatus.ACCEPTED.value
    }
    return result


# =========================================================
# ASYNC (CPU-bound) (Queue Thread)
# =========================================================

# Async Request
@router.get("/cpu-bound")
async def async_cpu_bound_request():

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
    loop = asyncio.get_running_loop()
    loop.run_in_executor(executor, cpu_bound_task, task_id)

    # response
    result = {
        "task_id": task_id,
        "status": TaskStatus.ACCEPTED.value
    }
    return result