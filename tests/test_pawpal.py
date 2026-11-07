from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def make_scheduler():
    owner = Owner("Jordan")
    pet = Pet("Biscuit")
    owner.add_pet(pet)
    return owner, pet, Scheduler(owner)


def test_mark_complete_changes_status():
    task = Task("Walk", "08:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Biscuit")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Walk", "08:00"))
    assert len(pet.tasks) == 1


def test_sort_by_time_is_chronological():
    _, pet, scheduler = make_scheduler()
    for time in ["18:00", "07:30", "12:15"]:
        pet.add_task(Task(f"Task {time}", time))
    times = [t.time for t in scheduler.sort_by_time()]
    assert times == ["07:30", "12:15", "18:00"]


def test_daily_task_creates_next_day_occurrence():
    _, pet, scheduler = make_scheduler()
    task = Task("Feed", "08:00", frequency="daily", due_date=date(2026, 11, 6))
    pet.add_task(task)
    follow_up = scheduler.mark_task_complete(task)
    assert follow_up.due_date == date(2026, 11, 7)
    assert follow_up.completed is False
    assert len(pet.tasks) == 2


def test_weekly_task_creates_occurrence_seven_days_later():
    _, pet, scheduler = make_scheduler()
    today = date.today()
    task = Task("Groom", "10:00", frequency="weekly", due_date=today)
    pet.add_task(task)
    follow_up = scheduler.mark_task_complete(task)
    assert follow_up.due_date == today + timedelta(days=7)


def test_one_time_task_does_not_recur():
    _, pet, scheduler = make_scheduler()
    task = Task("Vet visit", "09:00", frequency="once")
    pet.add_task(task)
    assert scheduler.mark_task_complete(task) is None
    assert len(pet.tasks) == 1


def test_conflict_detection_flags_same_time():
    owner, pet, scheduler = make_scheduler()
    other = Pet("Mochi", "cat")
    owner.add_pet(other)
    pet.add_task(Task("Walk", "07:30"))
    other.add_task(Task("Play", "07:30"))
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "07:30" in warnings[0]


def test_no_conflict_when_times_differ():
    _, pet, scheduler = make_scheduler()
    pet.add_task(Task("Walk", "07:30"))
    pet.add_task(Task("Feed", "08:00"))
    assert scheduler.detect_conflicts() == []


def test_pet_with_no_tasks_is_handled():
    _, _, scheduler = make_scheduler()
    assert scheduler.sort_by_time() == []
    assert scheduler.todays_schedule() == []
    assert scheduler.detect_conflicts() == []


def test_filter_by_pet_and_status():
    owner, pet, scheduler = make_scheduler()
    other = Pet("Mochi", "cat")
    owner.add_pet(other)
    walk = Task("Walk", "07:30")
    pet.add_task(walk)
    other.add_task(Task("Play", "09:00"))
    walk.mark_complete()
    assert [t.description for t in scheduler.filter_tasks(pet_name="Mochi")] == ["Play"]
    assert scheduler.filter_tasks(completed=True) == [walk]


def test_sort_by_priority_puts_high_first():
    _, pet, scheduler = make_scheduler()
    pet.add_task(Task("Low", "06:00", priority="low"))
    pet.add_task(Task("High", "20:00", priority="high"))
    assert scheduler.sort_by_priority()[0].description == "High"


# --- Stretch features: persistence and next available slot ---


def test_owner_round_trip_through_dict():
    owner, pet, _ = make_scheduler()
    pet.add_task(Task("Walk", "07:30", "daily", 30, "high", date(2026, 11, 6)))
    restored = Owner.from_dict(owner.to_dict())
    task = restored.get_all_tasks()[0]
    assert restored.name == "Jordan"
    assert task.pet_name == "Biscuit"
    assert task.due_date == date(2026, 11, 6)
    assert task.priority == "high"


def test_save_and_load_json(tmp_path):
    owner, pet, _ = make_scheduler()
    task = Task("Feed", "08:00", "weekly", 10, "low", date(2026, 11, 6))
    pet.add_task(task)
    task.mark_complete()
    path = tmp_path / "data.json"
    owner.save_to_json(str(path))
    loaded = Owner.load_from_json(str(path))
    assert len(loaded.pets) == 1
    assert loaded.get_all_tasks()[0].completed is True
    assert loaded.get_all_tasks()[0].frequency == "weekly"


def test_next_available_slot_on_empty_day_is_day_start():
    _, _, scheduler = make_scheduler()
    assert scheduler.next_available_slot(30, on=date(2026, 11, 6)) == "07:00"


def test_next_available_slot_skips_busy_time():
    _, pet, scheduler = make_scheduler()
    day = date(2026, 11, 6)
    pet.add_task(Task("Walk", "07:00", duration_minutes=30, due_date=day))
    pet.add_task(Task("Feed", "07:30", duration_minutes=15, due_date=day))
    assert scheduler.next_available_slot(20, on=day) == "07:45"


def test_next_available_slot_uses_gap_between_tasks():
    _, pet, scheduler = make_scheduler()
    day = date(2026, 11, 6)
    pet.add_task(Task("Walk", "07:00", duration_minutes=30, due_date=day))
    pet.add_task(Task("Groom", "09:00", duration_minutes=30, due_date=day))
    assert scheduler.next_available_slot(60, on=day) == "07:30"
    assert scheduler.next_available_slot(90, on=day) == "07:30"
    assert scheduler.next_available_slot(100, on=day) == "09:30"


def test_next_available_slot_ignores_completed_tasks():
    _, pet, scheduler = make_scheduler()
    day = date(2026, 11, 6)
    walk = Task("Walk", "07:00", duration_minutes=60, due_date=day)
    pet.add_task(walk)
    walk.mark_complete()
    assert scheduler.next_available_slot(30, on=day) == "07:00"


def test_next_available_slot_returns_none_when_day_is_full():
    _, pet, scheduler = make_scheduler()
    day = date(2026, 11, 6)
    pet.add_task(Task("Long task", "07:00", duration_minutes=840, due_date=day))
    assert scheduler.next_available_slot(15, on=day) is None
