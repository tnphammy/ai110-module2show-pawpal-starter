from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TaskType(Enum):
    WALK = "walk"
    FEEDING = "feeding"
    MEDS = "meds"
    ENRICHMENT = "enrichment"
    GROOMING = "grooming"


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Pet:
    name: str
    age: int
    breed: str

    def get_name(self) -> str:
        pass

    def set_name(self, name: str) -> None:
        pass

    def get_age(self) -> int:
        pass

    def set_age(self, age: int) -> None:
        pass

    def get_breed(self) -> str:
        pass

    def set_breed(self, breed: str) -> None:
        pass


@dataclass
class Owner:
    name: str
    pet: Optional["Pet"] = None

    def add_owner_name(self, name: str) -> None:
        pass

    def edit_owner_name(self, new_name: str) -> None:
        pass

    def add_pet(self, pet: Pet) -> None:
        pass

    def edit_pet(self, pet: Pet) -> None:
        pass


@dataclass
class Task:
    title: str
    duration_minutes: int
    type: TaskType
    priority: Priority

    def set_title(self, title: str) -> None:
        pass

    def set_duration(self, duration_minutes: int) -> None:
        pass

    def set_priority(self, priority: Priority) -> None:
        pass


@dataclass
class Scheduler:
    tasks: list[Task] = field(default_factory=list)
    total_available_minutes: int = 0

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def sort_tasks(self) -> None:
        pass

    def generate_plan(self) -> list[Task]:
        pass
