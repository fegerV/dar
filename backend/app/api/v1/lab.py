import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_db
from app.models.admin import AdminUser
from app.schemas.lab import (
    LabBenchmarkCreate,
    LabBenchmarkRead,
    LabBenchmarkResultUpdate,
    LabPhotoRead,
    LabRecipeProposalApprove,
    LabRecipeProposalRead,
    LabScenarioCreate,
    LabScenarioRead,
    LabStatsResponse,
)
from app.services.lab.service import LabService

router = APIRouter()


@router.get("/scenarios", response_model=list[LabScenarioRead])
async def list_scenarios(
    active_only: bool = Query(default=True),
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    service = LabService(db)
    return await service.list_scenarios(active_only=active_only)


@router.post("/scenarios", response_model=LabScenarioRead, status_code=status.HTTP_201_CREATED)
async def create_scenario(
    data: LabScenarioCreate,
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    service = LabService(db)
    return await service.create_scenario(data)


@router.get("/photos", response_model=list[LabPhotoRead])
async def list_photos(
    scenario_code: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    service = LabService(db)
    return await service.list_photos(scenario_code=scenario_code)


@router.post("/photos/upload", response_model=LabPhotoRead, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    filename: str,
    file_url: str,
    scenario_code: str | None = None,
    original_name: str | None = None,
    file_size_bytes: int | None = None,
    mime_type: str | None = None,
    width: int | None = None,
    height: int | None = None,
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    service = LabService(db)
    return await service.create_photo(
        filename=filename,
        file_url=file_url,
        scenario_code=scenario_code,
        original_name=original_name,
        file_size_bytes=file_size_bytes,
        mime_type=mime_type,
        width=width,
        height=height,
    )


@router.get("/benchmarks", response_model=list[LabBenchmarkRead])
async def list_benchmarks(
    scenario_id: uuid.UUID | None = Query(default=None),
    status: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    service = LabService(db)
    return await service.list_benchmarks(scenario_id=scenario_id, status=status)


@router.post("/benchmarks", response_model=LabBenchmarkRead, status_code=status.HTTP_201_CREATED)
async def create_benchmark(
    data: LabBenchmarkCreate,
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    service = LabService(db)
    return await service.create_benchmark(data)


@router.get("/benchmarks/{benchmark_id}", response_model=LabBenchmarkRead)
async def get_benchmark(
    benchmark_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    service = LabService(db)
    benchmark = await service.get_benchmark(benchmark_id)
    if not benchmark:
        raise HTTPException(status_code=404, detail="Benchmark not found")
    return benchmark


@router.patch("/benchmarks/{benchmark_id}/result", response_model=LabBenchmarkRead)
async def update_benchmark_result(
    benchmark_id: uuid.UUID,
    data: LabBenchmarkResultUpdate,
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    service = LabService(db)
    benchmark = await service.update_benchmark_result(benchmark_id, data)
    if not benchmark:
        raise HTTPException(status_code=404, detail="Benchmark not found")
    return benchmark


@router.post(
    "/benchmarks/{benchmark_id}/propose-recipe",
    response_model=LabRecipeProposalRead,
    status_code=status.HTTP_201_CREATED,
)
async def propose_recipe(
    benchmark_id: uuid.UUID,
    recipe_code: str,
    recipe_name: str,
    template_code: str,
    model_name: str,
    confidence_score: float | None = None,
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    service = LabService(db)
    benchmark = await service.get_benchmark(benchmark_id)
    if not benchmark:
        raise HTTPException(status_code=404, detail="Benchmark not found")
    return await service.create_recipe_proposal(
        benchmark_id=benchmark_id,
        recipe_code=recipe_code,
        recipe_name=recipe_name,
        template_code=template_code,
        model_name=model_name,
        confidence_score=confidence_score,
    )


@router.get("/proposals", response_model=list[LabRecipeProposalRead])
async def list_proposals(
    approved: bool | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    from sqlalchemy import select
    from app.models.lab import LabRecipeProposal

    stmt = select(LabRecipeProposal).order_by(LabRecipeProposal.created_at.desc())
    if approved is not None:
        stmt = stmt.where(LabRecipeProposal.approved == (1 if approved else 0))
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.patch("/proposals/{proposal_id}/approve", response_model=LabRecipeProposalRead)
async def approve_proposal(
    proposal_id: uuid.UUID,
    data: LabRecipeProposalApprove,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    service = LabService(db)
    proposal = await service.approve_recipe_proposal(
        proposal_id, data, approved_by=current_admin.email
    )
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal


@router.post("/proposals/{proposal_id}/apply", response_model=dict)
async def apply_proposal(
    proposal_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    service = LabService(db)
    success = await service.apply_proposal_to_production(proposal_id)
    if not success:
        raise HTTPException(status_code=400, detail="Proposal not found or not approved")
    return {"applied": True}


@router.get("/stats", response_model=LabStatsResponse)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    service = LabService(db)
    return await service.get_stats()


@router.post("/benchmarks/run-all", response_model=list[LabBenchmarkRead], status_code=status.HTTP_201_CREATED)
async def run_all_benchmarks(
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    service = LabService(db)
    scenarios = await service.list_scenarios(active_only=True)
    photos = await service.list_photos()
    models = [
        ("runway-gen3", "v1"),
        ("kling-1.6", "v1"),
        ("pika-2.0", "v1"),
        ("stable-video", "v1"),
    ]
    benchmarks: list[LabBenchmark] = []
    for scenario in scenarios:
        photo = next((p for p in photos if p.scenario_code == scenario.code), photos[0] if photos else None)
        for model_name, model_version in models:
            bm = await service.create_benchmark(
                LabBenchmarkCreate(
                    scenario_id=scenario.id,
                    photo_id=photo.id if photo else None,
                    model_name=model_name,
                    model_version=model_version,
                    cost_estimate=0.05,
                )
            )
            await service.update_benchmark_result(
                bm.id,
                LabBenchmarkResultUpdate(status="pending"),
            )
            benchmarks.append(bm)
    return benchmarks
