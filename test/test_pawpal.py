import pytest
from pawpal_system import Owner, Pet, Task, Scheduler, TaskType, Priority, FrequencyPeriod


# ---------------------------------------------------------------------------
# Fixtures — reusable objects shared across tests
# ---------------------------------------------------------------------------

@pytest.fixture
def basic_task():
    """A standard incomplete task used as a baseline."""
    return Task(
        title="Morning Walk",
        duration_minutes=30,
        type=TaskType.WALK,
        priority=Priority.HIGH,
        times_per_period=1,
        period=FrequencyPeriod.DAILY,
    )

@pytest.fixture
def another_task():
    """A second distinct task for isolation checks."""
    return Task(
        title="Feeding",
        duration_minutes=10,
        type=TaskType.FEEDING,
        priority=Priority.HIGH,
        times_per_period=2,
        period=FrequencyPeriod.DAILY,
    )

@pytest.fixture
def low_priority_task():
    """A low priority task useful for scheduler edge cases."""
    return Task(
        title="Brushing",
        duration_minutes=45,
        type=TaskType.GROOMING,
        priority=Priority.LOW,
        times_per_period=2,
        period=FrequencyPeriod.WEEKLY,
    )

@pytest.fixture
def empty_pet():
    """A pet with no tasks."""
    return Pet(name="Amie", age=3, breed="Stray Mix")

@pytest.fixture
def scheduler_with_pet(empty_pet):
    return Scheduler(total_available_minutes=60, pets=[empty_pet])


# ===========================================================================
# mark_complete() tests
# ===========================================================================

class TestMarkComplete:

    def test_completed_is_false_by_default(self, basic_task):
        """Tasks should start incomplete — completed must never default to True."""
        assert basic_task.completed is False

    def test_mark_complete_sets_completed_true(self, basic_task):
        """Core behavior: calling mark_complete() flips completed to True."""
        basic_task.mark_complete()
        assert basic_task.completed is True

    def test_mark_complete_twice_is_idempotent(self, basic_task):
        """
        Calling mark_complete() on an already-completed task should not raise
        or reset the flag. Tammy might tap 'done' twice by accident.
        """
        basic_task.mark_complete()
        basic_task.mark_complete()
        assert basic_task.completed is True

    def test_mark_complete_only_affects_that_task(self, basic_task, another_task):
        """
        Completing one task must not touch others on the same pet.
        Realistic case: Tammy finishes the walk but feeding is still pending.
        """
        pet = Pet(name="Amie", age=3, breed="Stray Mix")
        pet.add_task(basic_task)
        pet.add_task(another_task)

        basic_task.mark_complete()

        assert basic_task.completed is True
        assert another_task.completed is False

    def test_task_created_already_completed(self):
        """
        Edge case: a task initialized with completed=True.
        mark_complete() should leave it True, not toggle it.
        """
        task = Task(
            title="Pre-done Task",
            duration_minutes=5,
            type=TaskType.MEDS,
            priority=Priority.HIGH,
            times_per_period=1,
            period=FrequencyPeriod.DAILY,
            completed=True,
        )
        task.mark_complete()
        assert task.completed is True

    def test_completed_task_excluded_from_plan(self, basic_task, another_task, empty_pet):
        """
        Integration: generate_plan() must skip completed tasks entirely,
        even when there's plenty of time left for them.
        """
        empty_pet.add_task(basic_task)     # 30 min, HIGH
        empty_pet.add_task(another_task)   # 10 min, HIGH
        basic_task.mark_complete()

        scheduler = Scheduler(total_available_minutes=120, pets=[empty_pet])
        plan = scheduler.generate_plan()

        assert basic_task not in plan
        assert another_task in plan

    def test_completing_all_tasks_produces_empty_plan(self, basic_task, another_task, empty_pet):
        """
        Edge case: if every task is already done, the plan should be empty,
        not crash or return stale data.
        """
        empty_pet.add_task(basic_task)
        empty_pet.add_task(another_task)
        basic_task.mark_complete()
        another_task.mark_complete()

        scheduler = Scheduler(total_available_minutes=120, pets=[empty_pet])
        plan = scheduler.generate_plan()

        assert plan == []

    def test_completed_task_still_in_pet_task_list(self, basic_task, empty_pet):
        """
        Completing a task should not remove it from pet.tasks.
        The record stays — only the scheduler ignores it when planning.
        """
        empty_pet.add_task(basic_task)
        basic_task.mark_complete()

        assert basic_task in empty_pet.tasks


# ===========================================================================
# add_task() / task_count tests
# ===========================================================================

class TestTaskCount:

    def test_task_count_starts_at_zero(self, empty_pet):
        """A freshly created pet with no tasks should have task_count of 0."""
        assert empty_pet.task_count == 0

    def test_add_one_task_increments_count(self, empty_pet, basic_task):
        """Core behavior: adding one task bumps task_count to 1."""
        empty_pet.add_task(basic_task)
        assert empty_pet.task_count == 1

    def test_add_multiple_tasks_increments_each_time(self, empty_pet, basic_task, another_task, low_priority_task):
        """task_count should reflect every addition, not just the first."""
        empty_pet.add_task(basic_task)
        assert empty_pet.task_count == 1
        empty_pet.add_task(another_task)
        assert empty_pet.task_count == 2
        empty_pet.add_task(low_priority_task)
        assert empty_pet.task_count == 3

    def test_task_count_matches_len_of_tasks_list(self, empty_pet, basic_task, another_task):
        """
        task_count must always equal len(pet.tasks).
        If these drift apart, something is updating one but not the other.
        """
        empty_pet.add_task(basic_task)
        empty_pet.add_task(another_task)
        assert empty_pet.task_count == len(empty_pet.tasks)

    def test_remove_task_decrements_count(self, empty_pet, basic_task, another_task):
        """Removing a task should lower task_count, not leave it stale."""
        empty_pet.add_task(basic_task)
        empty_pet.add_task(another_task)
        empty_pet.remove_task(basic_task)
        assert empty_pet.task_count == 1
        assert empty_pet.task_count == len(empty_pet.tasks)

    def test_adding_to_one_pet_does_not_affect_another(self, basic_task):
        """
        Realistic case: Tammy has two pets. Adding a task to Amie must not
        change Biscuit's task_count. Counts are per-pet, not global.
        """
        amie = Pet(name="Amie", age=3, breed="Stray Mix")
        biscuit = Pet(name="Biscuit", age=7, breed="Golden Retriever")

        amie.add_task(basic_task)

        assert amie.task_count == 1
        assert biscuit.task_count == 0

    def test_add_same_task_object_twice(self, empty_pet, basic_task):
        """
        Ambiguous case: adding the exact same Task instance to a pet twice.
        Python lists allow duplicates, so task_count will reach 2 and the task
        will appear twice in pet.tasks. This is a known side effect of not
        guarding against duplicates in add_task(). Test documents current behavior.
        """
        empty_pet.add_task(basic_task)
        empty_pet.add_task(basic_task)

        assert empty_pet.task_count == 2
        assert len(empty_pet.tasks) == 2

    def test_pet_initialized_with_tasks_bypasses_count(self):
        """
        Tricky edge case: if you build a Pet with tasks=[...] directly in the
        constructor instead of using add_task(), task_count starts at 0 even
        though tasks already has items. Always use add_task() to stay consistent.
        """
        task = Task(
            title="Walk",
            duration_minutes=30,
            type=TaskType.WALK,
            priority=Priority.HIGH,
            times_per_period=1,
            period=FrequencyPeriod.DAILY,
        )
        pet = Pet(name="Amie", age=3, breed="Stray Mix", tasks=[task])

        # Documents the inconsistency — task_count is 0 but one task exists
        assert len(pet.tasks) == 1
        assert pet.task_count == 0  # task_count was never incremented via add_task()
