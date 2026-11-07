# PawPal+ (Module 2 Project)

PawPal+ is a Streamlit app that helps a pet owner plan daily care tasks for one or more pets. The logic lives in `pawpal_system.py` and is verified through a CLI demo (`main.py`) and a pytest suite before the UI (`app.py`) uses it.

## Features

- Add an owner, multiple pets, and tasks with time, duration, priority, and repeat frequency.
- Sort tasks by time or by priority.
- Filter tasks by pet and by completion status.
- Warn when two open tasks share the same date and time.
- Create the next occurrence automatically when a daily or weekly task is completed.
- Find the next free time slot for a task of a given length.
- Save and reload pets and tasks from a JSON file.

## Project Files

| File | Purpose |
| --- | --- |
| `pawpal_system.py` | `Task`, `Pet`, `Owner`, and `Scheduler` classes |
| `main.py` | CLI demo |
| `app.py` | Streamlit UI |
| `tests/test_pawpal.py` | pytest suite |
| `diagrams/uml_draft.mmd` | Phase 1 UML |
| `diagrams/uml_final.mmd` | Final UML matching the code |
| `reflection.md` | Design and AI strategy reflection |
| `ai_interactions.md` | Stretch feature documentation |

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
python -m streamlit run app.py
```

## Sample Output

Output of `python main.py`:

```text
=== PawPal+ for Jordan ===

Today's Schedule (sorted by time)
---------------------------------
  07:30  Biscuit  Morning walk        30 min  [high]  (daily, todo)
  07:30  Mochi    Play session        20 min  [medium]  (once, todo)
  08:00  Mochi    Give medication      5 min  [high]  (daily, todo)
  18:00  Biscuit  Evening walk        30 min  [medium]  (daily, todo)
  19:00  Mochi    Brush fur           15 min  [low]  (weekly, todo)

Sorted by priority
------------------
  07:30  Biscuit  Morning walk        30 min  [high]  (daily, todo)
  08:00  Mochi    Give medication      5 min  [high]  (daily, todo)
  07:30  Mochi    Play session        20 min  [medium]  (once, todo)
  18:00  Biscuit  Evening walk        30 min  [medium]  (daily, todo)
  19:00  Mochi    Brush fur           15 min  [low]  (weekly, todo)

Filter: Mochi only
------------------
  08:00  Mochi    Give medication      5 min  [high]  (daily, todo)
  19:00  Mochi    Brush fur           15 min  [low]  (weekly, todo)
  07:30  Mochi    Play session        20 min  [medium]  (once, todo)

Conflict check
--------------
  WARNING: Conflict on 2026-11-06 at 07:30: Morning walk (Biscuit), Play session (Mochi)

Next available slot
-------------------
  20 min task: 07:00
  60 min task: 08:05

Marking 'Morning walk' complete (daily task)
  Next occurrence created for 2026-11-07 at 07:30

Filter: completed tasks
-----------------------
  07:30  Biscuit  Morning walk        30 min  [high]  (daily, done)

Persistence
-----------
  Saved to demo_data.json and reloaded 2 pets, 6 tasks
```

The dates in this output reflect the day the demo was run.

## Smarter Scheduling

| Feature | Method(s) | Notes |
| --- | --- | --- |
| Sorting by time | `Scheduler.sort_by_time()` | Sorts by due date, then the `HH:MM` string. Zero-padded 24-hour times sort correctly as text. |
| Sorting by priority | `Scheduler.sort_by_priority()` | High first, then due date and time. |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)` | Either filter, both, or neither. Pet name is case-insensitive. |
| Today's plan | `Scheduler.todays_schedule()` | Open tasks due today, sorted by time. |
| Conflict handling | `Scheduler.detect_conflicts()` | Returns warning strings for open tasks with the same date and time. It never raises an error. |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.mark_task_complete()` | Daily adds 1 day and weekly adds 7 days using `timedelta`. One-time tasks do not repeat. |
| Next free slot | `Scheduler.next_available_slot()` | Uses task durations to find the earliest gap between 07:00 and 21:00 on a date. Returns `None` when the day is full. |

## Stretch Features

**Challenge 1, advanced algorithm:** `Scheduler.next_available_slot(duration_minutes, on, day_start, day_end)` sorts the open tasks for a date by start time and walks through them, moving a candidate start past each task that overlaps it. The Streamlit app shows the result under "Find a free time". The CLI output above shows 20-minute and 60-minute examples.

**Challenge 2, data persistence:** `Owner.save_to_json(path)` and `Owner.load_from_json(path)` write and read an owner, pets, and tasks. Each class has `to_dict()` and `from_dict()` methods that convert dates to ISO strings. The Streamlit app loads `data.json` on first load and saves after adding a pet, adding a task, or completing a task. If `data.json` is missing or unreadable, the app starts with an empty owner. Files modified: `pawpal_system.py`, `app.py`, `main.py`, `tests/test_pawpal.py`.

**Challenge 3, priority scheduling:** Each `Task` has a priority of `low`, `medium`, or `high`. `Scheduler.sort_by_priority()` sorts high first, then by due date and time. The "Sorted by priority" block in the CLI output above shows the result, with the high priority tasks listed before the medium and low ones.

## Testing PawPal+

Run the suite:

```bash
python -m pytest
```

The 18 tests cover task completion, adding tasks to a pet, chronological sorting, priority sorting, daily and weekly recurrence, one-time tasks not recurring, same-time conflict detection, no false conflicts, filtering by pet and status, a pet with no tasks, JSON save and load, and the next available slot (empty day, busy time, gaps, completed tasks, and a full day).

```text
============================= test session starts ==============================
platform linux -- Python 3.13.18, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/claude/pawpal
plugins: platformdirs-4.13.5, anyio-4.15.1
collected 18 items

tests/test_pawpal.py ..................                                  [100%]

============================== 18 passed in 0.03s ==============================
```

**Confidence Level: 4 of 5 stars.** The scheduling logic is covered by passing tests. The Streamlit UI has no automated tests, and conflict detection only checks exact time matches.

## Demo Walkthrough

1. Open the app with `python -m streamlit run app.py`. Enter an owner name.
2. Add a pet with a name and species. Add a second pet.
3. Add tasks for a pet with a time, duration, priority, and repeat setting.
4. If two open tasks share a time, a warning appears above the schedule table.
5. Use "Find a free time" to see the next open slot for a task of a given length.
6. Use the order, pet, and status controls to sort and filter the table.
7. Select a task and click Mark complete. A daily or weekly task creates its next occurrence.
8. Close and reopen the app. Pets and tasks load from `data.json`.

The CLI output in the Sample Output section shows the same sorting, filtering, conflict warning, recurrence, free slot, and persistence behavior.
