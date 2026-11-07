"""CLI demo for PawPal+. Run with: python main.py"""

from pawpal_system import Owner, Pet, Scheduler, Task


def print_tasks(title, tasks):
    print(f"\n{title}")
    print("-" * len(title))
    if not tasks:
        print("  (none)")
    for t in tasks:
        status = "done" if t.completed else "todo"
        print(
            f"  {t.time}  {t.pet_name:<8} {t.description:<18} "
            f"{t.duration_minutes:>3} min  [{t.priority}]  ({t.frequency}, {status})"
        )


def main():
    owner = Owner("Jordan")
    biscuit = Pet("Biscuit", "dog")
    mochi = Pet("Mochi", "cat")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # Tasks are added out of order on purpose.
    biscuit.add_task(Task("Evening walk", "18:00", "daily", 30, "medium"))
    biscuit.add_task(Task("Morning walk", "07:30", "daily", 30, "high"))
    mochi.add_task(Task("Give medication", "08:00", "daily", 5, "high"))
    mochi.add_task(Task("Brush fur", "19:00", "weekly", 15, "low"))
    # Same time as Biscuit's morning walk, to trigger a conflict warning.
    mochi.add_task(Task("Play session", "07:30", "once", 20, "medium"))

    scheduler = Scheduler(owner)

    print("=== PawPal+ for", owner.name, "===")
    print_tasks("Today's Schedule (sorted by time)", scheduler.todays_schedule())
    print_tasks("Sorted by priority", scheduler.sort_by_priority())
    print_tasks("Filter: Mochi only", scheduler.filter_tasks(pet_name="Mochi"))

    print("\nConflict check")
    print("--------------")
    for warning in scheduler.detect_conflicts() or ["No conflicts."]:
        print("  WARNING:", warning)

    print("\nNext available slot")
    print("-------------------")
    for minutes in (20, 60):
        slot = scheduler.next_available_slot(minutes)
        print(f"  {minutes} min task: {slot or 'no free slot today'}")

    print("\nMarking 'Morning walk' complete (daily task)")
    walk = biscuit.tasks[1]
    follow_up = scheduler.mark_task_complete(walk)
    print(f"  Next occurrence created for {follow_up.due_date} at {follow_up.time}")
    print_tasks("Filter: completed tasks", scheduler.filter_tasks(completed=True))

    print("\nPersistence")
    print("-----------")
    owner.save_to_json("demo_data.json")
    reloaded = Owner.load_from_json("demo_data.json")
    print(f"  Saved to demo_data.json and reloaded {len(reloaded.pets)} pets, "
          f"{len(reloaded.get_all_tasks())} tasks")


if __name__ == "__main__":
    main()
