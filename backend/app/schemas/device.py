from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DeviceCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=128, description="设备名称")
    image: str | None = Field(None, max_length=255, description="设备图片URL")
    model_spec: str | None = Field(None, max_length=255, description="型号规格")
    quantity: int = Field(1, ge=1, le=99999, description="数量")
    status: int = Field(1, description="状态(1正常/2维修)")
    lab_id: int = Field(..., description="所属实验室ID")


class DeviceUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128, description="设备名称")
    image: str | None = Field(None, max_length=255, description="设备图片URL")
    model_spec: str | None = Field(None, max_length=255, description="型号规格")
    quantity: int | None = Field(None, ge=1, le=99999, description="数量")
    status: int | None = Field(None, description="状态(1正常/2维修)")
    lab_id: int | None = Field(None, description="所属实验室ID")


class DeviceListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    image: str | None = None
    model_spec: str | None = None
    quantity: int
    status: int
    lab_id: int
    lab_name: str = ""
    create_time: datetime
