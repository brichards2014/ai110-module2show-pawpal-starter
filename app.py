"""PawPal+ Streamlit UI. Run with: streamlit run app.py"""

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Plan daily pet care, catch conflicts, and keep recurring tasks on track.")

# Streamlit reruns this script on every click, so the Owner lives in session_state.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Pet Owner")
owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

# --- Owner ---
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

# --- Add a pet ---
st.subheader("Add a pet")
with st.form("add_pet", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.error("Enter a pet name.")
        elif owner.get_pet(pet_name):
            st.warning(f"{pet_name} is already added.")
        else:
            owner.add_pet(Pet(pet_name.strip(), species))
            st.success(f"Added {pet_name.strip()}.")

if owner.pets:
    st.write("Pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))

# --- Add a task ---
st.subheader("Add a task")
if not owner.pets:
    st.info("Add a pet before scheduling tasks.")
else:
    with st.form("add_task", clear_on_submit=True):
        target = st.selectbox("Pet", [p.name for p in owner.pets])
        description = st.text_input("Task", value="Morning walk")
        col1, col2, col3 = st.columns(3)
        time_value = col1.time_input("Time")
        duration = col2.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        priority = col3.selectbox("Priority", ["high", "medium", "low"], index=1)
        frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
        if st.form_submit_button("Add task"):
            owner.get_pet(target).add_task(
                Task(
                    description=description.strip() or "Task",
                    time=time_value.strftime("%H:%M"),
                    frequency=frequency,
                    duration_minutes=int(duration),
                    priority=priority,
                )
            )
            st.success(f"Added '{description}' for {target}.")

# --- Schedule ---
st.subheader("Today's schedule")
for warning in scheduler.detect_conflicts():
    st.warning(f"{warning}. Move one of these tasks to a different time.")


def rows(tasks):
    return [
        {
            "Time": t.time,
            "Pet": t.pet_name,
            "Task": t.description,
            "Minutes": t.duration_minutes,
            "Priority": t.priority,
            "Repeats": t.frequency,
            "Done": t.completed,
        }
        for t in tasks
    ]


view = st.radio("Order by", ["Time", "Priority"], horizontal=True)
pet_filter = st.selectbox("Show pet", ["All"] + [p.name for p in owner.pets])
status_filter = st.selectbox("Show status", ["All", "Open", "Completed"])

tasks = scheduler.filter_tasks(
    pet_name=None if pet_filter == "All" else pet_filter,
    completed={"All": None, "Open": False, "Completed": True}[status_filter],
)
tasks = scheduler.sort_by_time(tasks) if view == "Time" else scheduler.sort_by_priority(tasks)

if tasks:
    st.table(rows(tasks))
else:
    st.info("No tasks match the current filters.")

# --- Complete a task ---
open_tasks = scheduler.sort_by_time(scheduler.filter_tasks(completed=False))
if open_tasks:
    st.subheader("Complete a task")
    labels = [f"{t.time} | {t.pet_name} | {t.description} ({t.due_date})" for t in open_tasks]
    choice = st.selectbox("Task", labels)
    if st.button("Mark complete"):
        done = open_tasks[labels.index(choice)]
        follow_up = scheduler.mark_task_complete(done)
        if follow_up:
            st.success(f"Done. Next {follow_up.frequency} task is set for {follow_up.due_date}.")
        else:
            st.success("Task marked complete.")
        st.rerun()
