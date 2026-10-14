from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.portfolio import Portfolio as PortfolioModel
from app.schemas.portfolio import Portfolio, PortfolioCreate, PortfolioUpdate

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


async def _get_or_404(session: AsyncSession, portfolio_id: int) -> PortfolioModel:
    project = await session.get(PortfolioModel, portfolio_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Portfolio project not found")
    return project


@router.get("", response_model=list[Portfolio])
async def list_portfolio(session: AsyncSession = Depends(get_session)):
    result = await session.scalars(select(PortfolioModel).order_by(PortfolioModel.id))
    return result.all()


@router.post("", response_model=Portfolio, status_code=201)
async def create_portfolio(payload: PortfolioCreate, session: AsyncSession = Depends(get_session)):
    project = PortfolioModel(**payload.model_dump())
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


@router.get("/{portfolio_id}", response_model=Portfolio)
async def get_portfolio(portfolio_id: int, session: AsyncSession = Depends(get_session)):
    return await _get_or_404(session, portfolio_id)


@router.patch("/{portfolio_id}", response_model=Portfolio)
async def update_portfolio(
    portfolio_id: int, payload: PortfolioUpdate, session: AsyncSession = Depends(get_session)
):
    project = await _get_or_404(session, portfolio_id)
    for field, value in payload.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(project, field, value)
    await session.commit()
    await session.refresh(project)
    return project


@router.delete("/{portfolio_id}", status_code=204)
async def delete_portfolio(portfolio_id: int, session: AsyncSession = Depends(get_session)):
    project = await _get_or_404(session, portfolio_id)
    await session.delete(project)
    await session.commit()
