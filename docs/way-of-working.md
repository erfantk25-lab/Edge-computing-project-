# Way of Working

## 1. Goals

The goal of our way of working is to:

* Develop the project towards a VG-level result
* Work in a structured and agile way
* Ensure that all team members actively contribute
* Share knowledge so that everyone understands the important parts of the project
* Deliver a functional and well-documented product

We focus on both **collaboration and learning**. No team member should only understand their own part of the project. Everyone should understand how their work connects to the overall system.

---

## 2. Working Hours

### Core Hours

All team members are expected to be available on weekdays between:

**10:00–15:00**

During the core hours, team members should be available for:

* Stand-up meetings
* Short meetings
* Problem solving
* Code reviews
* Collaborative work

Outside the core hours, everyone works flexibly according to their needs and agreements within the group.

---

## 3. Communication

### Daily Stand-up – 10:00

We have a short digital stand-up every working day.

Each team member answers:

1. What did I complete since the last meeting?
2. What am I working on today?
3. Do I have any blockers or need help?

**Time limit: 15 minutes.**

The stand-up should be short and focused. Longer technical discussions are handled separately after the meeting.

### Ongoing Communication

* Discord is used for quick communication during the day.
* GitHub Issues are used for tasks, problems and technical discussions.
* GitHub Pull Requests are used for code reviews and discussions about code.
* Larger technical questions are discussed in a short meeting when needed.

### End-of-Day Check-in – 14:45

We have a short check-in to discuss:

* What was completed today?
* What remains to be done?
* Are there any blockers for the next working day?

---

## 4. Division of Work

We work in parallel on different parts of the project, for example:

* Raspberry Pi Pico and MicroPython
* Sensors and hardware
* MQTT and Mosquitto
* Python consumer
* TimescaleDB
* Grafana
* Wokwi
* Documentation

Each task should have a responsible team member, but the implementation should be documented well enough for another team member to understand and take over when needed.

We help each other when necessary and avoid creating situations where only one person understands an important part of the system.

---

## 5. GitHub and Branching Strategy

We do not normally work directly on the `main` branch.

The `main` branch contains the stable version of the project.

For new functionality, we use feature branches:

```text
feature/pico-sensors
feature/mqtt
feature/consumer
feature/database
feature/grafana
feature/wokwi
feature/lcd
```

For documentation, we use branches such as:

```text
docs/readme
docs/way-of-working
```

For bug fixes, we use branches such as:

```text
fix/mqtt-reconnect
fix/sensor-reading
```

Branch names should clearly describe what is being developed or changed.

---

## 6. GitHub Issues

Larger tasks and problems are documented as GitHub Issues.

An Issue should contain:

* What needs to be done
* Why it needs to be done
* What is required for the task to be considered complete

Example:

```text
Issue: Implement MQTT communication

Tasks:
- Connect Pico W to Wi-Fi
- Connect Pico W to Mosquitto
- Publish sensor data
- Test MQTT communication
```

Issues are used together with our GitHub Project to track project progress.

---

## 7. Pull Requests

All code that is merged into `main` should go through a Pull Request.

The normal workflow is:

```text
Issue
  ↓
Branch
  ↓
Development
  ↓
Commit
  ↓
Push
  ↓
Pull Request
  ↓
Code Review
  ↓
Merge
```

Each Pull Request should:

* Have a clear title
* Describe what has been changed
* Be linked to the relevant Issue when possible
* Be as small and focused as possible

At least **one other team member** should review the Pull Request before it is merged into `main`.

---

## 8. Code Review

During code review, we check:

* Local verification: Check out the branch locally (gh pr checkout <PR#> or git checkout <branch>), run the code, and verify that it functions as expected.
* Does the solution work?
* Is the code easy to understand?
* Does the code follow the project structure?
* Is there unnecessary or duplicated code?
* Has the solution been tested?
* Does the documentation need to be updated?

Feedback should be constructive and focus on the code and solution rather than the person.

---

## 9. Commits

We make small and meaningful commits that describe a specific change.

We use the following structure:

```text
feat: new functionality
fix: bug fix
docs: documentation
test: tests
refactor: code restructuring
```

Examples:

```text
feat: add BME280 sensor
feat: publish sensor data using MQTT
fix: handle MQTT reconnect
docs: update README
test: add sensor validation
```

Commit messages should be short but clear.

---

## 10. Testing

New functionality should be tested before it is merged into `main`.

Depending on the functionality, testing can include:

* Physical hardware
* MicroPython
* Wokwi
* MQTT testing
* Database testing
* Grafana testing
* Integration testing

We test both individual components and the complete pipeline:

```text
Pico W
  ↓
Mosquitto
  ↓
Consumer
  ↓
TimescaleDB
  ↓
Grafana
```

---

## 11. Definition of Done

A task is considered complete when:

* The functionality has been implemented
* The solution has been tested
* The code is understandable
* Relevant documentation has been updated
* The Pull Request has been reviewed
* Review feedback has been addressed
* The changes have been merged into `main`

Only then should the task be moved to **Done** in our GitHub Project.

---

## 12. Code Quality

We aim to write code that is:

* Clear
* Simple
* Reusable
* Testable
* Easy to maintain

We follow the **DRY principle (Don't Repeat Yourself)** and avoid unnecessary duplication of code.

Functions and modules should have clear responsibilities.

---

## 13. Documentation

Important parts of the project should be documented continuously.

This includes, for example:

* README
* Architecture diagrams
* Wiring diagrams
* MQTT topics
* Database structure
* Installation instructions
* Wokwi simulation
* Grafana dashboard
* Hardware components and BOM

Documentation should be updated when the project implementation changes significantly.

---

## 14. AI and LLM Usage

LLM tools may be used for:

* Ideas and brainstorming
* Small parts of coding
* Debugging
* Explanations
* Documentation support

LLMs should not be used to build entire parts of the project without the team understanding the solution.

All AI-generated code must be reviewed, tested and understood by the team.

When LLMs are used for coding, this should be documented according to the course guidelines.

Example:

```python
# LLM-generated:
# Initial MQTT reconnect logic was generated with LLM assistance.
# The team reviewed, tested and modified the code.
```

The team remains responsible for all code included in the project.

---

## 15. Collaboration and Knowledge Sharing

All team members should have relevant commits and Pull Requests and actively contribute to the project.

We share knowledge by:

* Discussing technical decisions
* Performing code reviews
* Helping each other with blockers
* Documenting important solutions
* Making sure multiple team members understand the central parts of the project

The goal is for everyone to be able to present and explain the project during the final presentation.

---

## 16. Definition of Success

The project is considered successful when:

* All basic requirements are fulfilled
* The IoT pipeline works as an integrated system
* The repository is well structured
* All team members have contributed
* The project is well documented
* We can demonstrate the solution clearly
* We can explain our technical decisions and the problems we solved

