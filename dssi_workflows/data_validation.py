import time as ttime
from typing import Optional, Sequence, Str

from prefect import flow, get_run_logger, task
from tiled.client import from_profile


def get_validator_tasks() -> dict:
    return dict(read_all_streams=read_all_streams)


@task(retries=2, retry_delay_seconds=10)
def read_all_streams(beamline_acronym: Str, uid: Str):
    logger = get_run_logger()
    tiled_client = from_profile("nsls2", username=None)
    run = tiled_client[beamline_acronym]["raw"][uid]
    logger.info(f"Validating uid {run.start['uid']}")
    start_time = ttime.monotonic()
    for stream in run:
        logger.info(f"{stream}:")
        stream_start_time = ttime.monotonic()
        stream_data = run[stream].read()
        stream_elapsed_time = ttime.monotonic() - stream_start_time
        logger.info(f"{stream} elapsed_time = {stream_elapsed_time}")
        logger.info(f"{stream} nbytes = {stream_data.nbytes:_}")
    elapsed_time = ttime.monotonic() - start_time
    logger.info(f"{elapsed_time = }")


@flow
def general_data_validation(beamline_acronym: Str, uid: Str, validators: Optional[Sequence[Str]] = None):
    tasks = get_validator_tasks()
    validators = tasks.keys() if validators is None else validators
    for validator in validators:
        tasks[validator](beamline_acronym, uid)
