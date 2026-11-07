# PawPal+ Project Reflection

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
- These three additions came up while implementing recurrence and the schedule display, not from a separate review of the skeleton. I did not run a separate skeleton review step.

## 2. Scheduling Logic and Tradeoffs

**2a. Constraints**

The scheduler considers date, time, priority, completion status, and repeat frequency. Time and priority matter most because a missed medication costs more than a skipped play session.

**2b. Tradeoffs**

Conflict detection only checks for exact matches on date and time. A 30-minute walk at 07:30 and a 5-minute feeding at 07:45 overlap in real life, and the scheduler does not flag them. Exact matching is short and easy to test. Checking overlap needs start and end times for every task. That is a reasonable next step because `duration_minutes` is already stored.

## 3. AI Collaboration

- **Most effective features:** Generating the full class structure from the four-class plan saved the most time. Asking the assistant to write the CLI demo and tests together helped, because the demo output and the passing test run gave me two ways to check the same logic. I ran the tests and the Streamlit app on my own machine, since the assistant could not run Streamlit in its environment. The screenshot of the conflict warning is my own check of the UI.
- **One suggestion rejected or modified:** The assistant included conflict detection that only flags tasks with the same date and time. A more accurate version would check overlapping time ranges using `duration_minutes`. I kept the exact-match version because it is short, easy to test, and matches the assignment's example of a lightweight warning. I documented the tradeoff in section 2b.
- **Separate chat sessions per phase:** I did not use separate sessions. I worked in one conversation for the whole project, which kept the context together but meant design, code, tests, and documentation were all in one long thread. Separate sessions would have made it easier to review each phase on its own.
- **Lead architect takeaway:** The assistant produced working code quickly, but I still had to verify it. The tests passing and the UI behaving correctly were the evidence I relied on, and I checked the UI myself because the assistant could not. I also had to decide what to keep simple, such as exact-time conflicts, and what to leave for later.