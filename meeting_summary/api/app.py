from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI

from meeting_summary.api.routes.health import router as health_router
from meeting_summary.api.runtime import ApiRuntime
from meeting_summary.bootstrap import build_api_runtime
from meeting_summary.config import AppConfig

RuntimeFactory = Callable[[AppConfig], ApiRuntime]


def create_app(
    config: AppConfig | None = None,
    runtime_factory: RuntimeFactory = build_api_runtime,
) -> FastAPI:
    app_config = config or AppConfig()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        runtime = runtime_factory(app_config)
        app.state.runtime = runtime

        try:
            yield
        finally:
            runtime.shutdown()

    app = FastAPI(
        title="MeetMe Local API",
        lifespan=lifespan,
    )
    app.include_router(health_router, prefix="/api")
    return app


app = create_app()
