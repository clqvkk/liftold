from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ElevatorType(Enum):
    PASSENGER = "Пассажирский"
    CARGO = "Грузовой"
    PANTOGRAPH = "Пандусный"
    HOSPITAL = "Больничный"

class OrderStatus(Enum):
    NEW = "Новая"
    IN_PROGRESS = "В работе"
    COMPLETED = "Завершена"
    CANCELLED = "Отменена"

@dataclass
class ElevatorOrder:
    id: int = None
    customer_name: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    elevator_type: ElevatorType = ElevatorType.PASSENGER
    floors: int = 1
    capacity: int = 4
    installation_date: str = ""
    status: OrderStatus = OrderStatus.NEW
    created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    comments: str = ""
    priority: int = 1  # 1-5
    manager: str = ""
    price: float = 0.0