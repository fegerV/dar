from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.prompt_compiler import (
    CompilePromptRequest,
    PromptPlanResponse,
    VariableResolutionRequest,
    VariableResolutionResponse,
)
from app.services.prompt_compiler.service import PromptCompilerService

router = APIRouter(prefix="/prompt-compiler", tags=["Prompt Compiler"])


@router.post("/compile", response_model=PromptPlanResponse)
async def compile_prompt(
    body: CompilePromptRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PromptCompilerService(db)
    return await service.compile_prompt(body)


@router.post("/variables/resolve", response_model=VariableResolutionResponse)
async def resolve_variables(
    body: VariableResolutionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PromptCompilerService(db)
    return await service.resolve_variables(body)
