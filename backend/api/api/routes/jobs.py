from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.schemas.job import JobCreate, JobRead
from api.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["Jobs"])


def get_job_service(db: Session = Depends(get_db)) -> JobService:
    return JobService(db)


@router.post("", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreate,
    service: JobService = Depends(get_job_service),
) -> JobRead:
    return service.create_job(payload)


@router.get("", response_model=list[JobRead])
def list_jobs(service: JobService = Depends(get_job_service)) -> list[JobRead]:
    return service.list_jobs()


@router.get("/{job_id}", response_model=JobRead)
def get_job(
    job_id: int,
    service: JobService = Depends(get_job_service),
) -> JobRead:
    job = service.get_job(job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    service: JobService = Depends(get_job_service),
) -> None:
    deleted = service.delete_job(job_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
