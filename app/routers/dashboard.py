from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Service

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    query = (
        select(Service)
        .options(selectinload(Service.checks))
        .order_by(Service.created_at.desc())
    )
    services = db.scalars(query).all()
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"services": services},
    )
