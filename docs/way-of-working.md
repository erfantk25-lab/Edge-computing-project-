# Way of Working

## 1. Purpose

The purpose of this document is to define how our team collaborates during the PiCo Edge Computing project. It describes how we use GitHub, how we manage branches, commits and pull requests, and how we communicate and review each other's work.

Our goal is to work in an organized way where all team members contribute to the project and understand the code, hardware and documentation.

---

## 2. GitHub Repository

All project code, documentation and configuration files are stored in our shared GitHub repository.

The repository is organized into different folders for the different parts of the project.

Example:

```text
pico-edge-monitor/
│
├── pico/
├── consumer/
├── database/
├── grafana/
├── wokwi/
├── hardware/
├── docs/
└── README.md
```

The `main` branch contains the stable version of the project.

---

## 3. Branching Strategy

We do not normally work directly on the `main` branch.

Each feature or task should be developed in its own branch.

Examples:

```text
feature/pico-sensors
feature/mqtt
feature/consumer
feature/database
feature/grafana
feature/wokwi
feature/lcd
feature/azure
docs/way-of-working
docs/readme
```

Branch names should clearly describe what is being developed or changed.

For example:

```text
feature/mqtt
```

is used for MQTT-related development, while:

```text
docs/way-of-working
```

is used for documentation related to the way of working.

---

## 4. Issues

We use GitHub Issues to plan and track work.

Each larger task should have an Issue describing:

* What needs to be done
* Why it needs to be done
* What should be considered finished

Example:

```text
Issue: Implement MQTT communication

Tasks:
- Connect Pico W to Wi-Fi
- Connect Pico W to Mosquitto
- Publish sensor data
- Test MQTT messages
```

Issues are added to our GitHub Project so that the team can track progress.

---

## 5. GitHub Project

We use GitHub Projects to organize our work according to an agile workflow.

Our workflow is:

```text
Backlog → Todo → In Progress → Review → Done
```

Issues are moved between these stages as work progresses.

This gives the team an overview of what needs to be done, what is currently being worked on and what has been completed.

---

## 6. Commits

We make small and meaningful commits instead of putting many unrelated changes into one commit.

Commit messages should describe what was changed.

We use prefixes such as:

```text
feat: add BME280 sensor
fix: handle MQTT reconnect
docs: add way of working
test: add sensor validation
refactor: improve MQTT client
```

Examples:

```text
feat: add temperature sensor
feat: publish sensor data using MQTT
fix: handle Wi-Fi reconnect
docs: update README
```

Commits should be made regularly so that the development history is easy to understand.

---

## 7. Pull Requests

Changes should be merged into `main` through Pull Requests.

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

A Pull Request should contain:

* A clear title
* A short description of the changes
* The related Issue when possible
* Any relevant screenshots or test information

Example:

```text
Title:
Add MQTT communication

Description:
Implemented Wi-Fi and MQTT communication for the Raspberry Pi Pico W.
The Pico can now publish sensor data to the Mosquitto broker.
```

---

## 8. Code Review

At least one other team member should review a Pull Request before it is merged into `main`.

The reviewer checks:

* Does the code work?
* Is the code understandable?
* Does it follow the project structure?
* Are there unnecessary changes?
* Has the functionality been tested?
* Is documentation needed?

The author should respond to relevant review comments before merging.

---

## 9. Testing

New functionality should be tested before a Pull Request is merged.

Testing can include:

* Hardware testing
* Sensor testing
* MQTT testing
* Database testing
* Grafana testing
* Wokwi simulation
* Integration testing

For example, when implementing MQTT, we should verify that:

```text
Pico W
   ↓
Wi-Fi
   ↓
Mosquitto
   ↓
Consumer
```

works correctly before considering the task complete.

---

## 10. Hardware Changes

Hardware changes should also be documented.

When adding or changing a component, we should update the relevant documentation.

Examples:

* Wiring diagrams
* BOM
* README
* Hardware documentation

The team should also test the physical wiring before connecting the system to the complete IoT pipeline.

---

## 11. Documentation

Important parts of the project should be documented so that another team member can understand and reproduce the system.

Documentation may include:

* README
* Architecture diagrams
* Wiring diagrams
* Setup instructions
* Database structure
* MQTT topics
* Grafana configuration
* Wokwi simulation
* Hardware information

Documentation should be updated when the implementation changes significantly.

---

## 12. Communication

The team communicates regularly about project progress.

During meetings or short check-ins, each member should be able to explain:

1. What I completed
2. What I am working on
3. What problems or blockers I have

If a team member gets blocked, the issue should be communicated to the group rather than waiting until the end of the project.

---

## 13. Division of Work

Tasks are divided between team members, but important parts of the system should be understood by more than one person.

Possible areas of responsibility include:

* Hardware and sensors
* Raspberry Pi Pico and MicroPython
* MQTT and Mosquitto
* Python consumer
* TimescaleDB
* Grafana
* Wokwi
* Documentation

Team members can help each other when needed.

---

## 14. Definition of Done

A task is considered "Done" when:

* The implementation is completed
* The functionality has been tested
* The code/documentation is understandable
* Relevant documentation has been updated
* The Pull Request has been reviewed
* Review comments have been handled
* The Pull Request has been merged into `main`

An Issue should only be moved to `Done` when these conditions are fulfilled.

---

## 15. Code Quality

We aim to keep the code:

* Simple
* Readable
* Reusable
* Structured
* Easy to maintain

We follow the DRY principle (Don't Repeat Yourself) where appropriate.

Functions should have clear responsibilities, and duplicated code should be avoided when it can reasonably be replaced by reusable functions or modules.

---

## 16. AI and LLM Usage

LLMs may be used for small coding tasks, debugging support, explanations and idea generation.

LLMs should not be used to build entire project components without the team's understanding.

When AI-generated code is used, it should be reviewed, tested and understood by the team.

AI-generated code should be marked with a comment when appropriate, for example:

```python
# LLM-generated:
# Initial MQTT reconnect logic was generated with LLM assistance.
# The team reviewed, tested and modified the code.
```

The team remains responsible for all code included in the project.

---

## 17. Goal

Our goal is to develop the project collaboratively and professionally while making sure that every team member contributes to the project and understands the parts they work with.

The final system should be reproducible, documented and understandable by all team members.
