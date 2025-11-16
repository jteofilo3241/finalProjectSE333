# server.py
from fastmcp import FastMCP
import javalang
import os
import subprocess
import re
import json
import xml.etree.ElementTree as ET

mcp = FastMCP("Demo 🚀")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

def parse_java_methods(java_file_path):
    if not os.path.exists(java_file_path):
        return []

    methods = []
    content = open(java_file_path, "r").read()

    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content = re.sub(r'//.*', '', content)

    method_pattern = re.compile(
        r'(?:public|protected)\s+(?:static\s+)?(?:final\s+)?(?:<[\w, ? extends &]+>\s+)?'
        r'[\w\[\]<>]+\s+'
        r'(\w+)\s*'
        r'\((.*?)\)\s*'
        r'(?:throws\s+[\w, ]+)?\s*{',
        re.DOTALL
    )

    for match in method_pattern.finditer(content):
        name = match.group(1)
        params_raw = match.group(2).strip()
        params = []
        if params_raw:
            for p in params_raw.split(','):
                parts = p.strip().split()
                if parts:
                    param_name = parts[-1]
                    param_type = ' '.join(parts[:-1])
                    params.append({"name": param_name, "type": param_type})
        methods.append({"name": name, "params": params})

    return methods


@mcp.tool
def generate_and_run_tests(java_file_path: str) -> str:
    if not os.path.exists(java_file_path):
        return f"File not found: {java_file_path}"

    project_root = os.path.join(os.getcwd(), "codebase")
    class_name = os.path.splitext(os.path.basename(java_file_path))[0]
    methods = parse_java_methods(java_file_path)

    package_match = re.search(r'package\s+([\w.]+);', open(java_file_path).read())
    package = package_match.group(1) if package_match else None

    test_dir = os.path.join(project_root, "src", "test", "java")
    if package:
        test_dir = os.path.join(test_dir, *package.split('.'))
    os.makedirs(test_dir, exist_ok=True)

    test_class_name = class_name + "Test"
    test_methods = ""

    for method in methods:
        param_placeholders = []
        for p in method['params']:
            t = p['type']
            if t in ['int', 'short', 'byte', 'long']:
                param_placeholders.append("0")
            elif t in ['float', 'double']:
                param_placeholders.append("0.0")
            elif t == 'boolean':
                param_placeholders.append("false")
            else:
                param_placeholders.append("null")

        call_line = (
            f"{class_name} obj = new {class_name}();\n"
            f"        obj.{method['name']}({', '.join(param_placeholders)});"
        )

        test_methods += f"""
    @org.junit.jupiter.api.Test
    void test_{method['name']}() {{
        {call_line}
        // TODO: Add assertions
    }}
"""

    test_code = ""
    if package:
        test_code += f"package {package};\n\n"

    test_code += f"""
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class {test_class_name} {{
{test_methods}
}}
"""

    test_file_path = os.path.join(test_dir, f"{test_class_name}.java")
    with open(test_file_path, "w") as f:
        f.write(test_code)

    # Attempt to run Maven, but provide clearer diagnostics if the executable is missing
    try:
        result = subprocess.run(["mvn", "test"], cwd=project_root, capture_output=True, text=True)
    except FileNotFoundError:
        # On Windows, mvn might be installed as mvn.cmd - try that
        try:
            result = subprocess.run(["mvn.cmd", "test"], cwd=project_root, capture_output=True, text=True)
        except FileNotFoundError as e:
            return f"Error: Maven executable not found in PATH. Tried 'mvn' and 'mvn.cmd'. Exception: {e}"
        except Exception as e:
            return f"Error running 'mvn.cmd test': {e}"
    except Exception as e:
        return f"Error running 'mvn test': {e}"

    # If Maven ran, parse output for test summary and return stdout/stderr on failure
    summary = []
    for line in result.stdout.splitlines():
        if "Tests run:" in line:
            summary.append(line.strip())

    if summary:
        return "\n".join(summary)

    # No summary found — return both stdout and stderr for diagnostics
    out = result.stdout.strip()
    err = result.stderr.strip()
    if out or err:
        return "Maven ran but no test summary parsed.\nSTDOUT:\n" + out + "\nSTDERR:\n" + err

    return "Tests executed. Check Maven output for details."


def parse_jacoco_report(report_path):
    if not os.path.exists(report_path):
        return []

    tree = ET.parse(report_path)
    root = tree.getroot()
    uncovered = []

    for pkg in root.findall("package"):
        pkg_name = pkg.attrib.get("name")
        for cls in pkg.findall("class"):
            cls_name = cls.attrib.get("name")
            for line in cls.findall("line"):
                ci = int(line.attrib.get("ci", 0))
                mi = int(line.attrib.get("mi", 0))
                if ci == 0 and mi > 0:
                    uncovered.append(f"{pkg_name}.{cls_name} line {line.attrib['nr']}")

    return uncovered


def generate_coverage_recommendations(uncovered_lines):
    return [f"Add a test covering {line}" for line in uncovered_lines]


@mcp.tool
def analyze_coverage(report_path="target/site/jacoco/jacoco.xml"):
    uncovered_lines = parse_jacoco_report(report_path)
    if not uncovered_lines:
        return "All code is covered"
    return "\n".join(generate_coverage_recommendations(uncovered_lines))


@mcp.tool
def attempt_fix(java_file_path: str, failing_message: str) -> str:
    if not os.path.exists(java_file_path):
        return "Java file not found."

    src = open(java_file_path).read()

    if "NullPointerException" in failing_message:
        patched = src.replace("=", "= (", 1)
        open(java_file_path, "w").write(patched)
        return "Attempted simple null safety patch."

    return "Could not auto-fix; requires manual patch generation."


@mcp.tool
def run_iteration(java_file_path: str) -> str:
    dashboard = {}

    test_output = generate_and_run_tests(java_file_path)
    dashboard["test_output"] = test_output

    if "FAILURE" in test_output or "ERROR" in test_output:
        dashboard["bug_detected"] = True
        patch_result = attempt_fix(java_file_path, test_output)
        dashboard["fix_status"] = patch_result

        test_output = generate_and_run_tests(java_file_path)
        dashboard["post_fix_tests"] = test_output
    else:
        dashboard["bug_detected"] = False

    coverage_output = analyze_coverage("target/site/jacoco/jacoco.xml")
    dashboard["coverage"] = coverage_output

    return json.dumps(dashboard, indent=4)


@mcp.tool
def git_status() -> str:
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        return "✔ Working directory clean." if result.stdout.strip() == "" else "⚠ Changes detected:\n" + result.stdout
    except Exception as e:
        return f"Error running git status: {e}"


@mcp.tool
def git_add_all() -> str:
    ignore_patterns = ["target/", "generated-tests/", "*.class"]
    subprocess.run(["git", "add", "."])
    for patt in ignore_patterns:
        subprocess.run(["git", "reset", patt])
    staged = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True).stdout.strip()
    return "No files staged. (Ignored build artifacts?)" if staged == "" else "✔ Staged files:\n" + staged


@mcp.tool
def git_commit(message: str) -> str:
    if not message:
        return "Commit message cannot be empty."
    result = subprocess.run(["git", "commit", "-m", message], capture_output=True, text=True)
    return "Nothing to commit — working directory clean." if "nothing to commit" in result.stdout.lower() else "✔ Commit created:\n" + result.stdout


@mcp.tool
def git_push(remote: str = "origin", branch: str = "main") -> str:
    try:
        result = subprocess.run(["git", "push", remote, branch], capture_output=True, text=True)
        return "❌ Push failed:\n" + result.stderr if "fatal" in result.stderr.lower() else "✔ Push successful:\n" + result.stdout
    except Exception as e:
        return f"Push error: {e}"


@mcp.tool
def git_pull_request(base: str = "main", title: str = "Auto PR", body: str = "Generated by MCP agent") -> str:
    result = subprocess.run(["gh", "pr", "create", "--base", base, "--title", title, "--body", body],
                            capture_output=True, text=True)
    return "❌ Failed to create PR:\n" + result.stderr if result.returncode != 0 else "✔ Pull request created:\n" + result.stdout

@mcp.tool
def spec_based_test_generator(java_file_path: str) -> str:
    if not os.path.exists(java_file_path):
        return f"File not found: {java_file_path}"

    project_root = os.path.join(os.getcwd(), "codebase")
    class_name = os.path.splitext(os.path.basename(java_file_path))[0]
    methods = parse_java_methods(java_file_path)

    package_match = re.search(r'package\s+([\w.]+);', open(java_file_path).read())
    package = package_match.group(1) if package_match else None

    test_dir = os.path.join(project_root, "src", "test", "java")
    if package:
        test_dir = os.path.join(test_dir, *package.split('.'))
    os.makedirs(test_dir, exist_ok=True)

    test_class_name = class_name + "SpecTest"
    test_methods = ""

    for method in methods:
        for p in method['params']:
            if p['type'] in ['int', 'short', 'byte', 'long']:
                boundaries = [-1, 0, 1, 99, 100, 101]
            elif p['type'] in ['float', 'double']:
                boundaries = [-1.0, 0.0, 0.1, 99.9, 100.0, 101.0]
            elif p['type'] == 'boolean':
                boundaries = [True, False]
            else:
                boundaries = [None]
            for val in boundaries:
                call_line = f"{class_name} obj = new {class_name}();\n        obj.{method['name']}({val});"
                test_methods += f"""
    @org.junit.jupiter.api.Test
    void test_{method['name']}_{str(val).replace('.', '_').replace('-', 'neg')}() {{
        {call_line}
    }}
"""

    test_code = f"package {package};\n\n" if package else ""
    test_code += f"""
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class {test_class_name} {{
{test_methods}
}}
"""

    test_file_path = os.path.join(test_dir, f"{test_class_name}.java")
    with open(test_file_path, "w") as f:
        f.write(test_code)

    return f"Specification-based tests generated: {test_file_path}"
@mcp.tool
def ai_code_review(java_file_path: str) -> str:
    if not os.path.exists(java_file_path):
        return f"File not found: {java_file_path}"

    try:
        result = subprocess.run(
            ["spotbugs", "-textui", java_file_path],
            capture_output=True,
            text=True
        )
    except FileNotFoundError:
        return "SpotBugs not found. Please install SpotBugs and add it to PATH."
    except Exception as e:
        return f"Error running SpotBugs: {e}"

    issues = []
    for line in result.stdout.splitlines():
        if line.strip() and not line.startswith("Reading "):
            issues.append(line.strip())

    suggestions = []
    for issue in issues:
        if "Null" in issue:
            suggestions.append("Consider adding null checks for safety.")
        elif "Bad practice" in issue:
            suggestions.append("Refactor code to follow best practices.")
        elif "Unused" in issue:
            suggestions.append("Remove unused variables or methods.")
        else:
            suggestions.append("Review this warning manually.")

    return f"Found {len(issues)} issues.\n\nSuggestions:\n" + "\n".join(suggestions)


if __name__ == "__main__":
    mcp.run(transport="sse") 
