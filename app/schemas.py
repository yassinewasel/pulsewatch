from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class ServiceCreate(BaseModel):
    name: str
    url: HttpUrl


class ServiceRead(BaseModel):
    id: int
    name: str
    url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CheckResultRead(BaseModel):
    id: int
    service_id: int
    status: str
    status_code: int | None
    response_time_ms: float | None
    checked_at: datetime
    error_message: str | None

    model_config = ConfigDict(from_attributes=True)
