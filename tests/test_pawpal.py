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
