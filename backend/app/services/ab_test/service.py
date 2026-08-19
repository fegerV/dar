from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.models.ab_test import ABTest, ABTestVariant
from app.schemas.ab_test import (
    ABTestCreate,
    ABTestResponse,
    ABTestVariantCreate,
    ABTestVariantResponse,
)


class ABTestService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_test(self, body: ABTestCreate) -> ABTestResponse:
        if (
            body.start_date is not None
            and body.end_date is not None
            and body.start_date >= body.end_date
        ):
            raise ValidationException("start_date must be before end_date")

        test = ABTest(
            name=body.name,
            description=body.description,
            target=body.target,
            status="draft",
            traffic_allocation=body.traffic_allocation,
        )
        self.db.add(test)
        await self.db.flush()

        if not body.variants:
            raise ValidationException("At least one variant is required")

        for variant_data in body.variants:
            variant = ABTestVariant(
                test_id=test.id,
                code=variant_data.code,
                title=variant_data.title,
                config=variant_data.config,
                traffic_weight=variant_data.traffic_weight,
                is_control=variant_data.is_control,
            )
            self.db.add(variant)

        await self.db.flush()
        await self.db.commit()
        return await self._to_response(test.id)

    async def update_status(self, test_id: UUID, status: str) -> ABTestResponse:
        test = await self.db.get(ABTest, test_id)
        if not test:
            raise NotFoundException("A/B test not found")

        if status == "running" and test.status == "draft":
            test.start_date = datetime.now(UTC)
        if status == "completed":
            test.end_date = datetime.now(UTC)

        test.status = status
        await self.db.commit()
        return await self._to_response(test_id)

    async def get_test(self, test_id: UUID) -> ABTestResponse:
        return await self._to_response(test_id)

    async def list_tests(self) -> list[ABTestResponse]:
        result = await self.db.execute(select(ABTest).order_by(ABTest.created_at.desc()))
        tests = list(result.scalars().all())
        return [await self._to_response(t.id) for t in tests]

    async def get_variant_for_user(
        self, test_id: UUID, user_id: UUID
    ) -> ABTestVariantCreate | None:
        test = await self.db.get(ABTest, test_id)
        if not test or test.status != "running":
            return None

        now = datetime.now(UTC)
        if test.start_date and now < test.start_date:
            return None
        if test.end_date and now > test.end_date:
            return None

        hash_val = int(str(user_id)[:8], 16) % 100 + 1
        cumulative = 0
        variants_result = await self.db.execute(
            select(ABTestVariant).where(ABTestVariant.test_id == test_id)
        )
        variants = list(variants_result.scalars().all())

        for variant in variants:
            cumulative += variant.traffic_weight
            if hash_val <= cumulative:
                return ABTestVariantCreate(
                    code=variant.code,
                    title=variant.title,
                    config=variant.config,
                    is_control=variant.is_control,
                )
        return variants[-1] if variants else None

    async def record_result(
        self,
        test_id: UUID,
        variant_code: str,
        metric: str,
        value: float,
    ) -> None:
        from app.models.ab_test import ABTestResult

        result = ABTestResult(
            test_id=test_id,
            variant_code=variant_code,
            metric=metric,
            value=value,
            user_count=1,
            created_at=datetime.now(UTC),
        )
        self.db.add(result)
        await self.db.flush()

    async def get_variant_metrics(self, test_id: UUID) -> list[dict]:
        from app.models.ab_test import ABTestResult

        result = await self.db.execute(
            select(
                ABTestResult.variant_code,
                ABTestResult.metric,
                func.sum(ABTestResult.value).label("total"),
                func.count().label("samples"),
                func.sum(ABTestResult.user_count).label("users"),
            )
            .where(ABTestResult.test_id == test_id)
            .group_by(ABTestResult.variant_code, ABTestResult.metric)
        )
        return [
            {
                "variant_code": row.variant_code,
                "metric": row.metric,
                "total": float(row.total or 0),
                "samples": row.samples or 0,
                "users": row.users or 0,
                "conversion_rate": round((row.samples / row.users * 100) if row.users else 0, 2),
            }
            for row in result.all()
        ]

    async def _to_response(self, test_id: UUID) -> ABTestResponse:
        test = await self.db.get(ABTest, test_id)
        if not test:
            raise NotFoundException("A/B test not found")

        variants_result = await self.db.execute(
            select(ABTestVariant).where(ABTestVariant.test_id == test_id)
        )
        variants = list(variants_result.scalars().all())

        return ABTestResponse(
            id=test.id,
            name=test.name,
            description=test.description,
            target=test.target,
            status=test.status,
            traffic_allocation=test.traffic_allocation,
            start_date=test.start_date,
            end_date=test.end_date,
            variants=[
                ABTestVariantResponse.model_validate(v) for v in variants
            ],
            metrics=await self.get_variant_metrics(test_id),
        )
