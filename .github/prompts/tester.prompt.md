---
agent: "agent"
tools: ["generate_and_run_tests", "coverage_analysis", "git_status", "git_add_all", "git_commit", "git_push", "git_pull_request"]
description: "Test-generation agent for SE333."
model: "GPT-5 mini"
---


## Follow instruction below: ##
1. Use `generate_and_run_tests(java_file_path)` to generate JUnit tests for Java files.
2. Use `analyze_coverage(report_path)` to analyze Jacoco coverage and generate recommendations.
3. Use `git_status()`, `git_add_all()`, `git_commit(message)`, `git_push()`, `git_pull_request()` to manage Git workflows automatically.
4. Use `add(a, b)` for testing basic numeric addition if needed.
5. Always refer to the correct tool names exactly as listed in the `tools` array above.
6. Provide feedback, bug fixes, or coverage improvements by iterating with these tools.