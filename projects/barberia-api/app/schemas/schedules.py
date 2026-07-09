from datetime import time

from pydantic import BaseModel, Field, field_validator


class BusinessHoursDaySummary(BaseModel):
    weekday: int = Field(ge=1, le=7)
    open_time: time
    close_time: time
    is_closed: bool


class BusinessHoursListResponse(BaseModel):
    items: list[BusinessHoursDaySummary]


class BusinessHoursDayUpdate(BaseModel):
    weekday: int = Field(ge=1, le=7)
    open_time: time
    close_time: time
    is_closed: bool = False


class BusinessHoursUpdateRequest(BaseModel):
    items: list[BusinessHoursDayUpdate] = Field(min_length=1, max_length=7)

    @field_validator("items")
    @classmethod
    def validate_unique_weekdays(
        cls,
        items: list[BusinessHoursDayUpdate],
    ) -> list[BusinessHoursDayUpdate]:
        weekdays = [item.weekday for item in items]
        if len(weekdays) != len(set(weekdays)):
            raise ValueError("No puede haber días de la semana duplicados")
        return items


class BarberAvailabilityBlockSummary(BaseModel):
    weekday: int = Field(ge=1, le=7)
    start_time: time
    end_time: time
    is_active: bool


class BarberAvailabilityListResponse(BaseModel):
    items: list[BarberAvailabilityBlockSummary]


class BarberAvailabilityBlockUpdate(BaseModel):
    weekday: int = Field(ge=1, le=7)
    start_time: time
    end_time: time
    is_active: bool = True


class BarberAvailabilityUpdateRequest(BaseModel):
    items: list[BarberAvailabilityBlockUpdate] = Field(min_length=1, max_length=7)

    @field_validator("items")
    @classmethod
    def validate_unique_weekdays(
        cls,
        items: list[BarberAvailabilityBlockUpdate],
    ) -> list[BarberAvailabilityBlockUpdate]:
        weekdays = [item.weekday for item in items]
        if len(weekdays) != len(set(weekdays)):
            raise ValueError("No puede haber días de la semana duplicados")
        return items
