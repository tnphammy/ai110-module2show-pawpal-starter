from dataclasses import dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TaskType(Enum):
    """Categories of pet care tasks drawn directly from the README."""
    WALK = "walk"
    FEEDING = "feeding"
    MEDS = "meds"
    ENRICHMENT = "enrichment"
    GROOMING = "grooming"


class Priority(Enum):
    """
    Integer values allow direct comparison and sorting (higher = more urgent).
    e.g. Priority.HIGH > Priority.LOW evaluates cleanly using .value.
    """
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class FrequencyPeriod(Enum):
    """
    Represents the time window for a task's frequency.
    The integer value is the number of days in that period — this lets you
    normalize any frequency to a daily rate for sorting/comparison:

        daily_rate = times_per_period / period.value

    Example:
        "twice a day"  → times_per_period=2, period=DAILY  → rate = 2.0
        "twice a week" → times_per_period=2, period=WEEKLY → rate ≈ 0.29
    """
    DAILY = 1
    WEEKLY = 7
    MONTHLY = 30


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """
    A single pet care activity. This is the core unit the Scheduler works with.

    Design notes:
    - `title` is for display; `description` is for longer optional detail.
    - `duration_minutes` is in minutes — keep units consistent when summing
      against Scheduler.total_available_minutes.
    - Frequency is split into two fields (times_per_period + period) instead of
      a single value because "twice a day" and "twice a week" share the number 2
      but mean very different things. Normalize with: times_per_period / period.value
    - `completed` lets generate_plan() skip tasks already done today.
    """
    title: str
    duration_minutes: int
    type: TaskType
    priority: Priority
    times_per_period: int       # how many times the task occurs within the period
    period: FrequencyPeriod     # the time window: daily, weekly, or monthly

    # Optional fields with defaults — must come after required fields in dataclasses
    description: str = ""
    completed: bool = False

    def daily_rate(self) -> float:
        """Returns how often this task occurs per day — useful for sorting by urgency."""
        return self.times_per_period / self.period.value

    def set_title(self, title: str) -> None:
        self.title = title

    def set_description(self, description: str) -> None:
        self.description = description

    def set_duration(self, duration_minutes: int) -> None:
        self.duration_minutes = duration_minutes

    def set_priority(self, priority: Priority) -> None:
        self.priority = priority

    def set_frequency(self, times_per_period: int, period: FrequencyPeriod) -> None:
        """Set both frequency fields together to avoid them getting out of sync."""
        self.times_per_period = times_per_period
        self.period = period

    def mark_complete(self) -> None:
        self.completed = True


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """
    Stores pet info and owns the pet's task list.
    Pet is the single source of truth for its tasks — the Scheduler reads
    from Pet, it does not maintain a separate copy.
    """
    name: str
    age: int        # age in years; relevant for scheduling (e.g. senior pets, puppies)
    breed: str
    tasks: list[Task] = field(default_factory=list)
    task_count: int = 0     # mirrors len(self.tasks); kept in sync by add_task/remove_task

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)
        self.task_count += 1

    def remove_task(self, task: Task) -> None:
        self.tasks.remove(task)
        self.task_count -= 1

    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str) -> None:
        self.name = name

    def get_age(self) -> int:
        return self.age

    def set_age(self, age: int) -> None:
        self.age = age

    def get_breed(self) -> str:
        return self.breed

    def set_breed(self, breed: str) -> None:
        self.breed = breed


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    """
    Manages one or more pets and provides access to all of their tasks.
    Owner is a data container — scheduling logic lives in Scheduler, not here.
    """
    name: str
    pets: list[Pet] = field(default_factory=list)   # supports multiple pets

    def add_owner_name(self, name: str) -> None:
        self.name = name

    def edit_owner_name(self, new_name: str) -> None:
        self.name = new_name

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        self.pets.remove(pet)

    def get_all_tasks(self) -> list[Task]:
        """
        Aggregates tasks across all pets into a flat list.
        Useful for giving the Scheduler a flat view of everything that needs doing.
        """
        return [task for pet in self.pets for task in pet.tasks]


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

@dataclass
class Scheduler:
    """
    The brain of the system. Reads tasks from pets, applies constraints,
    and produces a daily plan.

    Design notes:
    - Scheduler holds pets (not tasks directly) because tasks live on Pet.
      This avoids duplicating task lists and keeps Pet as the single source
      of truth. Tasks are accessed via get_all_tasks().
    - total_available_minutes is the daily time budget. Without it, generate_plan()
      has no constraint and would just return everything — which defeats the purpose.
    - sort_tasks() and generate_plan() respect both Priority and daily_rate()
      when deciding what makes the cut.
    """
    total_available_minutes: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        self.pets.remove(pet)

    def get_all_tasks(self) -> list[Task]:
        """Collects tasks from every pet into a single flat list."""
        return [task for pet in self.pets for task in pet.tasks]

    def sort_tasks(self) -> list[Task]:
        """
        Returns tasks sorted by scheduling priority.
        Sort order: incomplete first, then Priority (desc), then daily_rate (desc),
        then duration (asc) as a tiebreaker to fit more tasks in the time budget.
        """
        return sorted(
            self.get_all_tasks(),
            key=lambda t: (t.completed, -t.priority.value, -t.daily_rate(), t.duration_minutes)
        )

    def generate_plan(self) -> list[Task]:
        """
        Selects tasks that fit within total_available_minutes.
        Skips completed tasks and stops adding once time runs out.

        Returns a flat list of Task objects that make up today's plan.
        To know which pet a task belongs to, check against pet.tasks in the caller.
        """
        plan = []
        time_used = 0
        for task in self.sort_tasks():
            if task.completed:
                continue
            if time_used + task.duration_minutes <= self.total_available_minutes:
                plan.append(task)
                time_used += task.duration_minutes
        return plan
