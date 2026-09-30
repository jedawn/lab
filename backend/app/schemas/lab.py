from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LabCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128, description="实验室名称")
    intro: str | None = Field(None, max_length=500, description="简介")
    cover: str | None = Field(None, max_length=255, description="封面图URL")
    location: str | None = Field(None, max_length=255, description="位置")
    capacity: int = Field(1, ge=1, le=9999, description="容纳人数")
    open_start: str | None = Field(None, max_length=5, description="开放开始时间(HH:MM)")
    open_end: str | None = Field(None, max_length=5, description="开放结束时间(HH:MM)")
    status: int = Field(1, description="状态(1正常/0禁用)")


class LabUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128, description="实验室名称")
    intro: str | None = Field(None, max_length=500, description="简介")
    cover: str | None = Field(None, max_length=255, description="封面图URL")
    location: str | None = Field(None, max_length=255, description="位置")
    capacity: int | None = Field(None, ge=1, le=9999, description="容纳人数")
    open_start: str | None = Field(None, max_length=5, description="开放开始时间(HH:MM)")
    open_end: str | None = Field(None, max_length=5, description="开放结束时间(HH:MM)")
    status: int | None = Field(None, description="状态(1正常/0禁用)")


class LabListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    intro: str | None = None
    cover: str | None = None
    location: str | None = None
    capacity: int
    open_start: str | None = None
    open_end: str | None = None
    status: int
    create_time: datetime
