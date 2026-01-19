"""
Send notifications to many users

via async function called `sendPushNotification`,
which sends a notification to a given `userId`.

user_ids = [1,2,3,4,5...];
sendPushNotification(userId) returns `True` if completed

"""
import asyncio
import logging
import random
from typing import Callable
from tenacity import (
    RetryError,
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_result,
)

from .utils.latency_simulation import io_bound_async

# from some_package import sendPushNotification, SomeExpectedPushNotificationError

RETRY_ATTEMPTS = 3
RETRY_MIN_TIME = 5  # seconds
RETRY_MAX_TIME = 15  # seconds


log = logging.getLogger(__name__)


class SomeExpectedPushNotificationError(Exception):
    """Some expected error while sending a push notification."""


async def sendPushNotification(user_id: int) -> bool:
    """Simulate: Send notification to user with variable duration 0-30 seconds"""
    duration = random.uniform(0, 4)
    await io_bound_async(duration)

    if user_id == 111:
        raise RuntimeError('Some Runtime Error')

    if random.random() < 0.8:
        return True
    elif random.random() < 0.5:
        raise SomeExpectedPushNotificationError("Error while sending a push notification")
    else:
        return False


async def _send_push_notification(user_id: int, worker_id: str) -> bool:
    """Wrapper around sendPushNotification."""
    try:
        result = await sendPushNotification(user_id)
    except SomeExpectedPushNotificationError:
        log.warning("[%s] ✗ Exception while sending notification to user_id=%s", worker_id, user_id)
        return False
    if not result:
        log.warning("[%s] ✗ Failed to send notification to user_id=%s", worker_id, user_id)
        return False
    else:
        log.info("[%s] ✓ Successfully sent notification to user_id=%s", worker_id, user_id)
        return True


def _log_on_retry(retry_state):
    """Custom before_sleep callback that logs the Retrying attempt."""
    log.warning(
        "Retrying for user_id=%s, attempt=%s",
        retry_state.args[0] if retry_state.args else 'unknown',
        retry_state.attempt_number
    )


@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=RETRY_MIN_TIME, max=RETRY_MAX_TIME),
    retry=retry_if_result(lambda x: not x),
    before_sleep=_log_on_retry,
    reraise=True
)
async def _send_push_notification_with_retry(user_id: int, worker_id: str) -> bool:
    """Wrapper around sendPushNotification with retry."""
    return await _send_push_notification(user_id, worker_id)


async def _delayed_retry(
        user_id: int, worker_id: str, processed_queue: asyncio.Queue, retry_semaphore: asyncio.Semaphore
):
    """Help function for applying a semahore and initial delay."""
    await asyncio.sleep(RETRY_MIN_TIME)

    async with retry_semaphore:
        try:
            result = await _send_push_notification_with_retry(user_id, worker_id)
            await processed_queue.put((user_id, result))
        except RetryError as e:
            await processed_queue.put((user_id, False))
            attempts = e.last_attempt.attempt_number
            log.error("[%s] user_id=%s failed after retries: %s. ", worker_id, user_id, attempts)


async def _push_notifications_worker(
        stop_event: asyncio.Event,
        queue: asyncio.Queue,
        processed_queue: asyncio.Queue,
        worker_id: str,
        on_retry_created: Callable[[asyncio.Task], None],
        retry_semaphore: asyncio.Semaphore
):
    """Main worker function."""
    while not stop_event.is_set():
        try:
            user_id = await asyncio.wait_for(queue.get(), timeout=0.1)
        except TimeoutError:
            continue

        try:
            success = await _send_push_notification(user_id, worker_id)
            if success:
                await processed_queue.put((user_id, success))
            else:
                # Create a task for Retry
                task = asyncio.create_task(_delayed_retry(
                    user_id=user_id,
                    worker_id="Retry",
                    processed_queue=processed_queue,
                    retry_semaphore=retry_semaphore
                ))
                on_retry_created(task)
        except Exception:
            log.exception("[%s] ✗ Unexpected error while sending notification to user_id=%s: %s", worker_id, user_id)
            await processed_queue.put((user_id, False))
        finally:
            queue.task_done()


async def send_notifications(
    user_ids: list[int],
    max_concurrent: int = 10,
    max_concurrent_retries: int = 5,
    queue_max_size: int = 1000
) -> dict:
    """Send push notifications to the users."""
    total = len(user_ids)
    # set `maxsize` for backpressure control
    queue = asyncio.Queue(maxsize=queue_max_size)
    processed_queue = asyncio.Queue()
    results = {}
    retry_workers = set()
    retry_semaphore = asyncio.Semaphore(max_concurrent_retries)

    # Callback to track retry tasks
    def on_retry_created(task: asyncio.Task):
        retry_workers.add(task)
        task.add_done_callback(retry_workers.discard)

    # Start workers
    stop_event = asyncio.Event()
    workers = []
    for i in range(max_concurrent):
        task = asyncio.create_task(
            _push_notifications_worker(
                stop_event=stop_event,
                queue=queue,
                processed_queue=processed_queue,
                worker_id=f"worker-{i}",
                on_retry_created=on_retry_created,
                retry_semaphore=retry_semaphore
            ))
        workers.append(task)

    # Add user IDs to a queue with backpressure control to manage memory usage
    user_id_iterator = iter(user_ids)
    try:
        for _ in range(queue_max_size):
            await queue.put(next(user_id_iterator))
    except StopIteration:
        pass

    for user_id in user_id_iterator:
        await queue.put(user_id)
        processed_id, processed_result = await processed_queue.get()
        results[processed_id] = processed_result

    # Wait for the queue to become processed
    await queue.join()

    # Stop workers
    stop_event.set()
    for worker in workers:
        await worker

    # Wait for all retry tasks to complete
    if retry_workers:
        await asyncio.gather(*retry_workers, return_exceptions=True)

    # Collect rest of results from the processed_queue
    try:
        while True:
            processed_id, processed_result = processed_queue.get_nowait()
            results[processed_id] = processed_result
    except asyncio.QueueEmpty:
        pass

    # Statistics
    successful = sum(results.values())
    failed = total - successful
    success_rate = (successful / total * 100) if total > 0 else 0

    log.info("Notification sending completed")
    log.info("Total processed: %d", total)
    log.info("Successful: %d (%.2f%%)", successful, success_rate)
    log.info("Failed: %d (%.2f%%)", failed, 100 - success_rate)

    return results


async def main():
    user_ids = list(range(1, 24))
    await send_notifications(user_ids, max_concurrent=4, queue_max_size=10)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)

    asyncio.run(main())
