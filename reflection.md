# PawPal+ Project Reflection

## 1. System Design

- The user should be able to add a pet and the relevant information about the pet.
- The user should be able to add and edit the task that they created with duration and priority.
- The user should be able to see all of their plans displayed.

**a. Initial design**

- Briefly describe your initial UML design.

    My initial UML had four classes: Owner, Pet, Task, and Scheduler. The idea was pretty straightforward — an owner has a pet, the scheduler holds a list of tasks, and tasks have a title, duration, type, and priority. I also included two enums, TaskType and Priority, to keep those values consistent across the system.

- What classes did you include, and what responsibilities did you assign to each?

    - **Owner** — holds the owner's name and a reference to their Pet. Responsible for adding and editing that info.
    - **Pet** — holds the pet's name, age, and breed. Basically a data container with getters and setters.
    - **Task** — represents a single care task. It knows its title, how long it takes (in minutes), what type it is (walk, feeding, meds, etc.), and how urgent it is (low, medium, high priority).
    - **Scheduler** — the brain of the system. It holds all the tasks and knows how much time is available in the day. It's responsible for adding/removing tasks, sorting them, and generating the daily plan.

**b. Design changes**

- Did your design change during implementation? 
- If yes, describe at least one change and why you made it.

    Yes, a few things were changed.
    
    - The biggest one was removing `Owner.age` — it is so normal and basic to me, but once I thought about it, the owner's age doesn't actually affect any scheduling logic. It was just extra data that didn't connect to anything. 
    - I removed the reference from Pet to Owner (originally `Pet` had an `owner` attribute). Having both classes point to each other created a circular logic that was unnecessary since the Owner already has the Pet, so the Pet doesn't need to know about the Owner too.
    - I also added in, and changed the name for, the duration attribute of the `Task` class to `total_available_minutes` to specify the unit to the Scheduler, which wasn't in the original plan. Without adding it as an argument, the scheduler would not have a constraint to fit the tasks in — it would just return everything, which defeats the whole purpose of a useful plan.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
