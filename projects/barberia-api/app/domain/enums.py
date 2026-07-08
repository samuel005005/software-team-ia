from enum import IntEnum, StrEnum


class UserRole(StrEnum):
    CLIENT = "client"
    BARBER = "barber"
    ADMIN = "admin"


class AppointmentStatus(StrEnum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"
    NO_SHOW = "no_show"


class Weekday(IntEnum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7
