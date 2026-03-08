## Team Overrides

These instructions are user-owned and take priority as repository-specific working rules.

## Rules

- `Documentation`: Always update documentation for meaningful code changes that affect behavior, APIs, configuration, setup, workflows, architecture, or user-visible output.
- `Testing`: Always add or update tests for meaningful code changes. For logic changes, add multiple tests covering the main path, edge cases, and at least one regression case.
- `Testing`: Use the existing relevant test suite when one exists. If no suitable test setup exists, propose a minimal setup first and only implement it after user confirmation.
- `Frontend Verification`: For frontend changes, verify the result visually. Prefer taking a screenshot yourself and checking the implemented result. If that is not possible, say so clearly and do not claim verification.
- `Docker`: If the repository uses Docker or docker-compose, ask before running tests whether to run them in Docker or locally, unless the project already has a confirmed preference. If the first run fails and the environment may be the reason, ask before retrying in the other environment.
- `Change Quality`: Prefer root-cause fixes. Keep changes aligned with existing project conventions unless the user asks otherwise.
- `Reporting`: If a change does not justify a test or documentation update, say that explicitly in the final response.
