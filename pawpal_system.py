"""PawPal+ logic layer: Task, Pet, Owner, and Scheduler classes."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
RECURRING = {"daily": 1, "weekly": 7}


def _to_minutes(hhmm: str) -> int:
    """Convert an 'HH:MM' string to minutes after midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def _to_hhmm(total_minutes: int) -> str:
    """Convert minutes after midnight to an 'HH:MM' string."""
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


@dataclass
class Task:
    """A single pet care activity."""

    description: str
    time: str  # "HH:MM", 24-hour
    frequency: str = "once"  # "once", "daily", or "weekly"
    duration_minutes: int = 15
    priority: str = "medium"  # "low", "medium", or "high"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    pet_name: str = ""

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> Optional["Task"]:
        """Return a new task for the next daily or weekly occurrence, or None for one-time tasks."""
        days = RECURRING.get(self.frequency)
        if days is None:
            return None
        return Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            due_date=self.due_date + timedelta(days=days),
            pet_name=self.pet_name,
        )

    def to_dict(self) -> dict:
        """Return a JSON-friendly dictionary for this task."""
        return {
            "description": self.description,
            "time": self.time,
            "frequency": self.frequency,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "due_date": self.due_date.isoformat(),
            "completed": self.completed,
            "pet_name": self.pet_name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Build a task from a dictionary created by to_dict()."""
        return cls(
            description=data["description"],
            time=data["time"],
            frequency=data.get("frequency", "once"),
            duration_minutes=data.get("duration_minutes", 15),
            priority=data.get("priority", "medium"),
            due_date=date.fromisoformat(data["due_date"]),
            completed=data.get("completed", False),
            pet_name=data.get("pet_name", ""),
        )


@dataclass
class Pet:
    """A pet and the tasks assigned to it."""

    name: str
    species: str = "dog"
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and record the pet's name on the task."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        self.tasks.remove(task)

    def to_dict(self) -> dict:
        """Return a JSON-friendly dictionary for this pet and its tasks."""
        return {
            "name": self.name,
            "species": self.species,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """Build a pet and its tasks from a dictionary created by to_dict()."""
        pet = cls(name=data["name"], species=data.get("species", "dog"))
        for task_data in data.get("tasks", []):
            pet.add_task(Task.from_dict(task_data))
        return pet


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        """Find a pet by name (case-insensitive), or return None."""
        for pet in self.pets:
            if pet.name.lower() == name.lower():
                return pet
        return None

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def to_dict(self) -> dict:
        """Return a JSON-friendly dictionary for this owner, pets, and tasks."""
        return {"name": self.name, "pets": [p.to_dict() for p in self.pets]}

    @classmethod
    def from_dict(cls, data: dict) -> "Owner":
        """Build an owner from a dictionary created by to_dict()."""
        owner = cls(name=data["name"])
        for pet_data in data.get("pets", []):
            owner.add_pet(Pet.from_dict(pet_data))
        return owner

    def save_to_json(self, path: str = "data.json") -> None:
        """Write this owner's pets and tasks to a JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, path: str = "data.json") -> "Owner":
        """Read an owner, pets, and tasks from a JSON file written by save_to_json()."""
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


class Scheduler:
    """Retrieves, organizes, and manages tasks across an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks from the owner's pets."""
        return self.owner.get_all_tasks()

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Sort tasks by due date, then by HH:MM time."""
        tasks = self.get_all_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda t: (t.due_date, t.time))

    def sort_by_priority(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Sort tasks by priority (high first), then by due date and time."""
        tasks = self.get_all_tasks() if tasks is None else tasks
        return sorted(
            tasks, key=lambda t: (PRIORITY_RANK.get(t.priority, 1), t.due_date, t.time)
        )

    def filter_tasks(
        self, pet_name: Optional[str] = None, completed: Optional[bool] = None
    ) -> List[Task]:
        """Filter tasks by pet name and/or completion status. None means no filter."""
        result = self.get_all_tasks()
        if pet_name is not None:
            result = [t for t in result if t.pet_name.lower() == pet_name.lower()]
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        return result

    def todays_schedule(self, on: Optional[date] = None) -> List[Task]:
        """Return incomplete tasks due on the given date (default today), sorted by time."""
        on = on or date.today()
        due = [t for t in self.get_all_tasks() if t.due_date == on and not t.completed]
        return self.sort_by_time(due)

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Complete a task. For daily or weekly tasks, add the next occurrence to the same pet."""
        task.mark_complete()
        follow_up = task.next_occurrence()
        if follow_up is not None:
            pet = self.owner.get_pet(task.pet_name)
            if pet is not None:
                pet.add_task(follow_up)
        return follow_up

    def next_available_slot(
        self,
        duration_minutes: int,
        on: Optional[date] = None,
        day_start: str = "07:00",
        day_end: str = "21:00",
    ) -> Optional[str]:
        """Return the earliest 'HH:MM' start with a free gap long enough, or None if the day is full."""
        on = on or date.today()
        busy = sorted(
            (_to_minutes(t.time), _to_minutes(t.time) + t.duration_minutes)
            for t in self.get_all_tasks()
            if t.due_date == on and not t.completed
        )
        candidate = _to_minutes(day_start)
        limit = _to_minutes(day_end)
        for start, end in busy:
            if candidate + duration_minutes <= start:
                break
            candidate = max(candidate, end)
        if candidate + duration_minutes <= limit:
            return _to_hhmm(candidate)
        return None

    def detect_conflicts(self) -> List[str]:
        """Return warning messages for incomplete tasks that share the same date and time."""
        slots: dict = {}
        for task in self.get_all_tasks():
            if task.completed:
                continue
            slots.setdefault((task.due_date, task.time), []).append(task)
        warnings = []
        for (day, time), group in sorted(slots.items()):
            if len(group) > 1:
                names = ", ".join(f"{t.description} ({t.pet_name})" for t in group)
                warnings.append(f"Conflict on {day} at {time}: {names}")
        return warnings
