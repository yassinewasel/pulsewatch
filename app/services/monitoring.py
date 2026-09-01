from time import perf_counter

import httpx
from sqlalchemy.orm import Session

from app.models import CheckResult, Service

REQUEST_TIMEOUT_SECONDS = 10.0


def check_service(db: Session, service: Service) -> CheckResult:
    started_at = perf_counter()

    try:
        response = httpx.get(service.url, timeout=REQUEST_TIMEOUT_SECONDS, follow_redirects=False)
        response_time_ms = round((perf_counter() - started_at) * 1000, 2)
        result = CheckResult(
            service_id=service.id,
            status="UP" if 200 <= response.status_code < 400 else "DOWN",
            status_code=response.status_code,
            response_time_ms=response_time_ms,
        )
    except httpx.RequestError as exc:
        result = CheckResult(
            service_id=service.id,
            status="DOWN",
            error_message=str(exc),
        )

    db.add(result)
    db.commit()
    db.refresh(result)
    return result
