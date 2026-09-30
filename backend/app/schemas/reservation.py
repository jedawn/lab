from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReservationCreateRequest(BaseModel):
    lab_id: int = Field(..., description="实验室ID")
    device_id: int | None = Field(None, description="设备ID(为空表示预约整个实验室)")
    date: str = Field(..., min_length=1, max_length=10, description="预约日期(YYYY-MM-DD)")
    start_time: str | None = Field(None, max_length=5, description="开始时间(HH:MM)")
    end_time: str | None = Field(None, max_length=5, description="结束时间(HH:MM)")
    remark: str | None = Field(None, max_length=500, description="备注")


class ReservationAuditRequest(BaseModel):
    status: int = Field(..., description="审核结果(2通过/3拒绝)")


class ReservationListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    user_name: str = ""
    lab_id: int
    lab_name: str = ""
    device_id: int | None = None
    device_name: str = ""
    date: str
    start_time: str | None = None
    end_time: str | None = None
    remark: str | None = None
    status: int
    create_time: datetime
