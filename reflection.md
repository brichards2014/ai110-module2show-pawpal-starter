# PawPal+ Project Reflection

Items marked **[YOUR NOTES]** describe your own experience with your AI assistant. Fill those in with what actually happened before you submit.

## 1. System Design

**Three core actions**

- Add a pet to an owner profile.
- Schedule a care task (walk, feeding, medication) for a pet with a time, duration, priority, and repeat setting.
- See today's tasks in order, with warnings for conflicts.

**1a. Initial design**

- `Task` is a dataclass holding a description, time, frequency, completion status, and later duration, priority, and due date. It can mark itself complete.
- `Pet` is a dataclass holding a name, species, and a list of tasks. It adds and removes tasks.
- `Owner` holds a list of pets and returns all tasks across them.
- `Scheduler` takes an owner and handles sorting, filtering, conflict detection, and recurrence. The data classes hold data and the scheduler holds the logic.

**1b. Design changes**

- Added `pet_name` to `Task` so the scheduler can show which pet a task belongs to and find the right pet when creating a recurring task.
- Added `due_date` to `Task`. Time alone cannot tell today's walk from tomorrow's, which recurrence requires.
- Added `Task.next_occurrence()` so recurrence logic sits with the task and the scheduler only decides when to call it.
- **[YOUR NOTES]** Describe which of these changes came from your AI assistant's review of the skeleton.

## 2. Scheduling Logic and Tradeoffs

**2a. Constraints**

The scheduler considers date, time, priority, completion status, and repeat frequency. Time and priority matter most because a missed medication costs more than a skipped play session.

**2b. Tradeoffs**

Conflict detection only checks for exact matches on date and time. A 30-minute walk at 07:30 and a 5-minute feeding at 07:45 overlap in real life, and the scheduler does not flag them. Exact matching is short and easy to test. Checking overlap needs start and end times for every task. That is a reasonable next step because `duration_minutes` is already stored.

## 3. AI Collaboration

- **Most effective features:** **[YOUR NOTES]**
- **One suggestion rejected or modified:** **[YOUR NOTES]** Describe a specific suggestion, what you changed, and why.
- **Separate chat sessions per phase:** **[YOUR NOTES]**
- **Lead architect takeaway:** **[YOUR NOTES]**
