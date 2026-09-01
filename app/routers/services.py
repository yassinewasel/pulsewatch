from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CheckResult, Service
from app.schemas import CheckResultRead, ServiceCreate, ServiceRead
from app.services.monitoring import check_service

router = APIRouter(prefix="/api/services", tags=["services"])


def get_service_or_404(db: Session, service_id: int) -> Service:
    service = db.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.get("", response_model=list[ServiceRead])
def list_services(db: Session = Depends(get_db)) -> list[Service]:
    return list(db.scalars(select(Service).order_by(Service.created_at.desc())))


@router.post("", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
def create_service(payload: ServiceCreate, db: Session = Depends(get_db)) -> Service:
    service = Service(name=payload.name.strip(), url=str(payload.url))
    if not service.name:
        raise HTTPException(status_code=422, detail="Service name cannot be empty")
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(service_id: int, db: Session = Depends(get_db)) -> Response:
    service = get_service_or_404(db, service_id)
    db.delete(service)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{service_id}/check", response_model=CheckResultRead)
def run_check(service_id: int, db: Session = Depends(get_db)) -> CheckResult:
    return check_service(db, get_service_or_404(db, service_id))


@router.post("/check-all", response_model=list[CheckResultRead])
def run_all_checks(db: Session = Depends(get_db)) -> list[CheckResult]:
    services = db.scalars(select(Service).order_by(Service.id)).all()
    return [check_service(db, service) for service in services]


@router.get("/{service_id}/checks", response_model=list[CheckResultRead])
def list_checks(service_id: int, db: Session = Depends(get_db)) -> list[CheckResult]:
    get_service_or_404(db, service_id)
    query = (
        select(CheckResult)
        .where(CheckResult.service_id == service_id)
        .order_by(CheckResult.checked_at.desc())
    )
    return list(db.scalars(query))
