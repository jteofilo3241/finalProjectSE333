SE333 MCP Testing Agent

Description:
This project implements an MCP (Modular Code Processor) testing agent for automated Java test generation, code analysis, and AI-assisted code review. It supports generating JUnit tests, running them with Maven, and providing actionable insights for software development workflows.
able of Contents

MCP Tool API

Installation & Configuration

Usage Examples

Troubleshooting & FAQ
MCP Tool API

All MCP tools are implemented under the serv2 server namespace.

generate_and_run_tests

Description: Generates JUnit tests for a specified Java file and runs them using Maven.

Parameters:

java_file_path: str — Path to the Java source file.

Returns: str — Test summary or diagnostic message.
analyze_coverage

Description: Analyzes test coverage of the project using Maven's coverage plugins.

Parameters: None

Returns: str — Summary of coverage analysis.

git_status

Description: Returns the current Git repository status.

Parameters: None

Returns: str — Git status output.

git_add_all

Description: Stages all changes in the Git repository.

Parameters: None

Returns: str — Success/failure message.

git_commit

Description: Commits staged changes to Git.

Parameters:

message: str — Commit message

Returns: str — Commit result.

git_push

Description: Pushes committed changes to the remote repository.

Parameters: None

Returns: str — Push result.

git_pull_request

Description: Creates a pull request on the configured remote repository.

Parameters:

title: str — PR title

body: str — PR description

Returns: str — PR URL or error.

run_iteration

Description: Executes a full development iteration (generate tests → run → analyze coverage → apply fixes).

Parameters: None

Returns: str — Iteration summary.

attempt_fix

Description: Applies automated fixes based on test failures or coverage gaps.

Parameters: None

Returns: str — Fix result.

spec_based_test_generator

Description: Generates tests based on specification techniques (boundary value, equivalence classes, decision tables).

Parameters:

java_file_path: str — Path to Java file

Returns: str — Generated test file path or summary.

ai_code_review

Description: Performs static analysis, code smell detection, and style guide enforcement using AI and existing tools (SpotBugs, PMD).

Parameters:

java_file_path: str — Path to Java file

Returns: str — Review report with suggestions.

Installation & Configuration

Install Prerequisites

Python 3.11+

Maven 3.9+ (mvn -v to verify installation)

Java JDK 21+

Set up Project

Clone the repository to a local folder.

Ensure the pom.xml file is located in the codebase folder.

Navigate to the project root (FinalProjectSE) in the terminal.

Install Python Dependencies

pip install -r requirements.txt


Configure MCP Server

Ensure servers.json contains only relevant MCP servers, e.g., serv2.

Q: Maven executable not found
A: Ensure Maven is installed and in your PATH. On Windows, mvn.cmd may be required.

Q: Tests fail with ClassNotFoundException
A: Ensure the Java source files are correctly placed under codebase/src/main/java and your package declarations match folder structure.

Q: MCP tools do not appear in the agent
A: Make sure each tool has a description entry in servers.json and is correctly namespaced under serv2.
