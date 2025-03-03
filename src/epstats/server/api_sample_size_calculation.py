import logging
from fastapi import APIRouter, Depends, HTTPException
from statsd import StatsClient
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..toolkit.statistics import Statistics

from .req import SampleSizeCalculationData
from .res import SampleSizeCalculationResult


_logger = logging.getLogger("epstats")


def get_sample_size_calculation_router(get_executor_pool, get_statsd) -> APIRouter:
    def _sample_size_calculation(data: SampleSizeCalculationData, statsd: StatsClient):
        try:

            if data.std is None:
                f = Statistics.required_sample_size_per_variant_bernoulli
            else:
                f = Statistics.required_sample_size_per_variant

            sample_size_per_variant = f(**data.dict())

            _logger.info((f"Calculation finished, sample_size_per_variant = {sample_size_per_variant}."))
            return SampleSizeCalculationResult(sample_size_per_variant=sample_size_per_variant)
        except Exception as e:
            _logger.error(f"Cannot calculate the sample size because of: '{e}'")
            _logger.exception(e)
            statsd.incr("errors.sample_size_calculation")
            raise HTTPException(
                status_code=500,
                detail=f"Cannot calculate the sample size because of: '{e}'",
            )

    router = APIRouter()

    @router.post("/sample-size-calculation", response_model=SampleSizeCalculationResult)
    async def sample_size_calculation(
        data: SampleSizeCalculationData,
        evaluation_pool: ThreadPoolExecutor = Depends(get_executor_pool),
        statsd: StatsClient = Depends(get_statsd),
    ):
        """
        Calculates sample size based on `data`.
        """
        _logger.info(f"Calling the sample size calculation with {data.json()}")
        statsd.incr("requests.sample_size_calculation")
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(evaluation_pool, _sample_size_calculation, data, statsd)

    return router
