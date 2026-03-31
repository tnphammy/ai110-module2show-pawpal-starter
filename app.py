import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, TaskType, Priority, FrequencyPeriod

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# ---------------------------------------------------------------------------
# Step 1 — Owner
# Creates the Owner once and stores it in the vault. Pets and tasks hang off
# of owner.pets, so this is the root of the entire data tree.
# ---------------------------------------------------------------------------

st.subheader("Owner")

owner_name = st.text_input("Owner name", value="Jordan")

if st.button("Save owner"):
    st.session_state.owner = Owner(name=owner_name)

if "owner" in st.session_state:
    st.caption(f"Owner saved: **{st.session_state.owner.name}**")

st.divider()

# ---------------------------------------------------------------------------
# Step 2 — Pets
# Each submission appends a new Pet to owner.pets via add_pet().
# owner.pets is the single source of truth — no parallel pet list needed.
# ---------------------------------------------------------------------------

st.subheader("Pets")

if "owner" not in st.session_state:
    st.info("Save an owner first before adding pets.")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
    with col3:
        pet_breed = st.text_input("Breed", value="Mixed")

    if st.button("Add pet"):
        new_pet = Pet(name=pet_name, age=int(pet_age), breed=pet_breed)
        st.session_state.owner.add_pet(new_pet)

    if st.session_state.owner.pets:
        st.write("Your pets:")
        st.table([
            {"Name": p.name, "Age": p.age, "Breed": p.breed, "Tasks": p.task_count}
            for p in st.session_state.owner.pets
        ])

st.divider()

# ---------------------------------------------------------------------------
# Step 3 — Tasks
# The pet selector maps the chosen name back to the actual Pet object in
# owner.pets so we can call pet.add_task() on the right one.
# st.session_state.tasks is only used for the display table below.
# ---------------------------------------------------------------------------

st.subheader("Tasks")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "owner" not in st.session_state or not st.session_state.owner.pets:
    st.info("Add at least one pet before adding tasks.")
else:
    # Build a name → Pet object lookup so the dropdown selection is useful
    pet_map = {p.name: p for p in st.session_state.owner.pets}

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        target_pet_name = st.selectbox("For pet", list(pet_map.keys()))
    with col2:
        task_title = st.text_input("Task title", value="Morning walk")
    with col3:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col4:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col5:
        task_type = st.selectbox("Type", [t.value for t in TaskType])

    # Second row — frequency fields are kept together since they only make
    # sense as a pair: "2 times per WEEKLY" reads as "twice a week"
    col6, col7 = st.columns(2)
    with col6:
        times_per_period = st.number_input("Times per period", min_value=1, max_value=30, value=1)
    with col7:
        period = st.selectbox("Period", [p.name.capitalize() for p in FrequencyPeriod])

    if st.button("Add task"):
        target_pet = pet_map[target_pet_name]
        target_pet.add_task(Task(
            title=task_title,
            duration_minutes=int(duration),
            type=TaskType(task_type),
            priority=Priority[priority.upper()],
            times_per_period=int(times_per_period),
            period=FrequencyPeriod[period.upper()],  # maps "Daily" back to FrequencyPeriod.DAILY
        ))
        # Mirror to display table so the user sees it immediately
        st.session_state.tasks.append({
            "Pet": target_pet_name,
            "Task": task_title,
            "Duration (min)": int(duration),
            "Priority": priority,
            "Type": task_type,
            "Frequency": f"{int(times_per_period)}x / {period.lower()}",
        })

    if st.session_state.tasks:
        st.write("All tasks:")
        st.table(st.session_state.tasks)
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Step 4 — Generate Schedule
# Passes owner.pets directly to Scheduler — all pets and their tasks are
# included automatically. No changes needed here as more pets are added.
# ---------------------------------------------------------------------------

st.subheader("Build Schedule")

available_minutes = st.number_input(
    "Time available today (minutes)", min_value=1, max_value=480, value=90
)

if st.button("Generate schedule"):
    if "owner" not in st.session_state or not st.session_state.owner.pets:
        st.warning("Save your owner and add at least one pet with tasks first.")
    elif not any(p.tasks for p in st.session_state.owner.pets):
        st.warning("Add at least one task to a pet before generating a schedule.")
    else:
        scheduler = Scheduler(
            total_available_minutes=int(available_minutes),
            pets=st.session_state.owner.pets,   # all pets, not just one
        )
        plan = scheduler.generate_plan()

        if not plan:
            st.info("No tasks fit in the available time, or all tasks are already complete.")
        else:
            st.success(f"Plan generated — {sum(t.duration_minutes for t in plan)} / {available_minutes} min used")

            # Map task id back to pet name for display
            task_to_pet = {id(task): pet.name for pet in st.session_state.owner.pets for task in pet.tasks}
            st.table([
                {
                    "Pet": task_to_pet.get(id(t), "—"),
                       "Task": t.title,
                    "Type": t.type.value,
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority.name,
                }
                for t in plan
            ])
