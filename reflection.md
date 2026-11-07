# PawPal+ Project Reflection

## 1. System Design

**Three core actions**

- Add a pet to an owner's profile.
- Schedule a care task (walk, feeding, medication) for a pet with a time, duration, priority, and repeat setting.
- View today's scheduled tasks in order, including warnings when scheduling conflicts occur.

**1a. Initial design**

- `Task` is a dataclass that stores the task description, scheduled time, frequency, and completion status. Additional attributes were introduced as the project developed, including duration, priority, and due date. It also supports marking a task as complete.
- `Pet` is a dataclass that stores the pet's name, species, and associated tasks. It supports adding and removing tasks.
- `Owner` maintains a list of pets and provides access to all tasks associated with those pets.
- `Scheduler` is responsible for organizing tasks, filtering them by date, detecting scheduling conflicts, and handling recurring tasks.

The design separates data management from scheduling logic. The `Task`, `Pet`, and `Owner` classes manage the application's information, while `Scheduler` handles the operations performed on that information.

**1b. Design changes**

- Added `pet_name` to `Task` so that scheduled tasks could be associated with the correct pet. This also helped the scheduler identify which pet should receive a recurring task.
- Added `due_date` to `Task` because storing only a time was not enough to distinguish between tasks scheduled for different days.
- Added `Task.next_occurrence()` to keep recurrence calculations within the `Task` class instead of placing all the responsibility on the scheduler.

**My experience with the AI assistant:** These changes came from the agent's review and development of the initial class structure. As the implementation progressed, the agent identified information that the original design was missing, particularly the need to associate tasks with specific pets and dates. I reviewed the proposed changes and their purpose before continuing with the expanded implementation. The changes helped make recurring tasks and daily scheduling more practical without placing all the functionality into one class.

## 2. Scheduling Logic and Tradeoffs

**2a. Constraints**

The scheduler considers the task date, scheduled time, priority, completion status, and repeat frequency. These details help determine which tasks should appear in the daily schedule and whether a conflict exists.

Priority is particularly important because not all care tasks have the same level of importance. For example, missing a scheduled medication could have more serious consequences than delaying a play session. The application therefore needs to make task priorities visible when organizing daily responsibilities.

**2b. Tradeoffs**

The current conflict detection checks for tasks with the exact same date and scheduled time. This approach is straightforward to implement and test, but it does not identify every possible scheduling conflict.

For example, a 30-minute walk scheduled for 7:30 AM and a five-minute feeding scheduled for 7:45 AM would overlap, even though their start times are different. The current implementation would not flag this situation.

I accepted this simpler approach for the project because it provided a working conflict-detection feature without making the scheduling logic unnecessarily complicated. However, I recognize that checking whether task start and end times overlap would be a better solution. Since `duration_minutes` is already stored for each task, this could be added as a future improvement.

## 3. AI Collaboration

- **Most effective features:** The most useful part of working with the AI assistant was its ability to generate an initial implementation and then help improve it through testing and troubleshooting. It created the main project files, ran the initial demonstration and tests, and helped resolve issues when I attempted to run the application on my Windows machine. When I shared my terminal output, it identified the problems and provided corrections. Its later review of my uploaded project was also valuable because it discovered that `pawpal_system.py` was empty, which explained why the tests were failing. It also helped expand the project with additional functionality, including finding the next available scheduling slot and saving and loading data through JSON.

- **One suggestion rejected or modified:** I did not completely reject any major implementation suggestions, but I did question the results when one of the additional tests failed. The test expected a 90-minute task not to fit into a 90-minute available window. After reviewing the issue, the agent identified that the test's expected result was incorrect and corrected it. I accepted the correction because the original expectation did not match the intended scheduling behavior. I also accepted the exact date-and-time conflict detection approach while documenting its limitations and possible improvements.

- **Separate chat sessions per phase:** I used one conversation throughout the project instead of creating separate sessions for design, implementation, testing, and documentation. This helped maintain context because the agent could refer back to earlier decisions and code changes. However, as the conversation became longer, it sometimes became more difficult to track individual changes and review earlier decisions. In a future project, I would consider separating major development phases while keeping a record of the important decisions and requirements.

- **Lead architect takeaway:** This project showed me that using an AI assistant to develop software does not remove the need to understand, review, and test the application. Although the agent generated most of the code, I was responsible for guiding the work, providing feedback, running the application in my own environment, and deciding whether the results met the requirements. Testing on my Windows machine revealed issues that could not be identified in the agent's cloud environment, particularly command differences and the Streamlit interface. The discovery of the empty `pawpal_system.py` file was another important lesson. It showed me that I cannot rely only on successful-looking test results or generated documentation. I need to inspect the actual files, understand the changes being made, and independently verify the final deliverables before submitting a project.