from pydantic import BaseModel, Field


class ExecuteRequestData(BaseModel):
    session_id: str = Field(..., description="UUID сессии участника для GWT-запроса")


class ExecuteResponseData(BaseModel):
    success: bool
    message: str
    target_status_code: int | None = None
    target_response_preview: str | None = None
