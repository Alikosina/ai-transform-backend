from fastapi import APIRouter

router = APIRouter(prefix="/mock", tags=["mock"])


@router.get("")
def get_mock():
    return {"message": "Автодеплой работает", "version": "1.0.0"}
