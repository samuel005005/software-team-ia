from pydantic import BaseModel, ConfigDict


class EntitySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    detail: str


class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
