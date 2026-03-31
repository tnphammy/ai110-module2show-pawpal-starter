from pawpal_system import Owner, Pet, Task, Scheduler, TaskType, Priority, FrequencyPeriod

# ---------------------------------------------------------------------------
# Set up pets
# ---------------------------------------------------------------------------

amie = Pet(name="Amie", age=3, breed="Stray Mix")
biscuit = Pet(name="Biscuit", age=7, breed="Golden Retriever")

# ---------------------------------------------------------------------------
# Set up tasks
# Amie's tasks
# ---------------------------------------------------------------------------

morning_walk = Task(
    title="Morning Walk",
    duration_minutes=30,
    type=TaskType.WALK,
    priority=Priority.HIGH,
    times_per_period=1,
    period=FrequencyPeriod.DAILY,
    description="30-minute walk around the block before breakfast."
)

feeding = Task(
    title="Feeding",
    duration_minutes=10,
    type=TaskType.FEEDING,
    priority=Priority.HIGH,
    times_per_period=2,         # twice a day → daily_rate = 2.0
    period=FrequencyPeriod.DAILY,
)

enrichment = Task(
    title="Enrichment Play",
    duration_minutes=20,
    type=TaskType.ENRICHMENT,
    priority=Priority.MEDIUM,
    times_per_period=1,
    period=FrequencyPeriod.DAILY,
    description="Puzzle toy or sniff game to keep Amie mentally stimulated."
)

amie.add_task(morning_walk)
amie.add_task(feeding)
amie.add_task(enrichment)

# ---------------------------------------------------------------------------
# Biscuit's tasks
# ---------------------------------------------------------------------------

meds = Task(
    title="Medication",
    duration_minutes=5,
    type=TaskType.MEDS,
    priority=Priority.HIGH,
    times_per_period=1,
    period=FrequencyPeriod.DAILY,
    description="Joint supplement — hide in peanut butter."
)

grooming = Task(
    title="Brushing",
    duration_minutes=45,
    type=TaskType.GROOMING,
    priority=Priority.LOW,
    times_per_period=2,         # twice a week → daily_rate ≈ 0.29
    period=FrequencyPeriod.WEEKLY,
)

biscuit.add_task(meds)
biscuit.add_task(grooming)

# ---------------------------------------------------------------------------
# Set up owner and scheduler
# ---------------------------------------------------------------------------

tammy = Owner(name="Tammy")
tammy.add_pet(amie)
tammy.add_pet(biscuit)

# Simulate Tammy already completing the morning walk before running the scheduler.
# mark_complete() sets task.completed = True, which causes generate_plan() to skip it.
morning_walk.mark_complete()

# 90 minutes available today — grooming (45 min) may or may not fit
scheduler = Scheduler(total_available_minutes=90, pets=tammy.pets)
plan = scheduler.generate_plan()

# Build a set of planned task ids for fast membership checks when grouping by pet
planned_ids = {id(task) for task in plan}
time_used = sum(task.duration_minutes for task in plan)

# Separate already-completed tasks from tasks that simply didn't fit in the time budget
already_done = [task for task in scheduler.get_all_tasks() if task.completed]
didnt_fit = [task for task in scheduler.get_all_tasks() if not task.completed and id(task) not in planned_ids]

# ---------------------------------------------------------------------------
# Print Today's Schedule
# ---------------------------------------------------------------------------

LINE = "=" * 52
print(f"\n{LINE}")
print(f"  Today's Schedule  —  Owner: {tammy.name}")
print(f"  Time budget: {scheduler.total_available_minutes} min")
print(LINE)

for pet in tammy.pets:
    pet_plan = [t for t in pet.tasks if id(t) in planned_ids]
    if not pet_plan:
        continue
    print(f"\n  {pet.name} ({pet.breed}, age {pet.age})")
    print(f"  {'-' * 40}")
    for task in pet_plan:
        freq = f"{task.times_per_period}x/{task.period.name.lower()}"
        print(f"  [ ] {task.title:<22} {task.duration_minutes:>3} min  |  {task.priority.name:<6}  |  {freq}")
        if task.description:
            print(f"      Note: {task.description}")

print(f"\n{LINE}")
print(f"  Time used : {time_used} / {scheduler.total_available_minutes} min")

if already_done:
    print(f"  Already done: {', '.join(t.title for t in already_done)}")
if didnt_fit:
    print(f"  Didn't fit: {', '.join(t.title for t in didnt_fit)}")

print(LINE)
