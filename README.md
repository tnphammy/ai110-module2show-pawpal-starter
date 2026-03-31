# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

### Smarter Scheduling
These are the scheduling features I implemented with the help of Claude Code!

1. **Priority-based knapsack selection** — Instead of just grabbing tasks in order until time runs out, the scheduler uses a knapsack algorithm to find the combination of tasks with the highest total priority that actually fits within the available time budget. This means a long, low-priority task won't accidentally block two shorter, more important ones from getting into the plan.

2. **Conflict detection and time-slot assignment** — Once the best set of tasks is selected, each one gets assigned a real start time. If two tasks for the same pet would overlap, the second one gets bumped to the next open slot automatically. A warning message explains what happened and where the task moved to, so nothing silently disappears from the schedule.

3. **Sorting and filtering the plan** — After the plan is generated, you can sort today's tasks by start time (earliest or latest first) and filter by completion status (pending or done) or by which pet the task belongs to. Sorting only applies to today's tasks since future tasks don't have time slots yet.

4. **Interval-based recurrence** — Every task tracks when it was last completed. From that, it calculates its next due date by dividing the period length by how many times it repeats — for example, a task done twice a week becomes due again in 3.5 days. Tasks that have never been completed are treated as due immediately. This is what drives the whole upcoming section.

5. **Multi-day plan grouped by due date** — Instead of producing one flat list for today, the scheduler builds a 30-day lookahead grouped by date. Today's section runs the full knapsack and time-slot logic. Future sections just show which tasks are coming up and when, based on each task's next due date. When a task is marked done, the plan regenerates immediately and the next occurrence appears in the right future date section automatically.

