import subprocess
import json
from tabulate import tabulate
import sys
import ast
import time
import os


# url = "https://raw.githubusercontent.com/justinejay01/TheColorGame/refs/heads/master/app.py"
# response = requests.get(url)
# with open("app.py", "w") as f:
#     f.write(response.text)
# print("Downloaded app.py from GitHub.") 


checks = {
    "Type Check": ["mypy", "--ignore-missing-imports", "./"],
    "Lint Check": ["flake8", "./"],
    "Code Style Check": ["pycodestyle", "./"],
    "Formatting Check": ["black", "--check", "./"]
}

results = {}
exit_code = 0


for check_name, command in checks.items():
    try:
        process = subprocess.run(command, capture_output=True, text=True)
        output = process.stdout.strip() + "\n" + process.stderr.strip()
        violations = []
        status = "Passed"

        if process.returncode != 0:
            status = "Failed"
            exit_code = 1
            # Parse violations line by line
            for line in output.split("\n"):
                if line.strip():
                    violations.append(line.strip())

        results[check_name] = {
            "status": status,
            "violations": violations,
            "count": len(violations)
        }

    except FileNotFoundError:
        results[check_name] = {
            "status": "Tool Not Installed",
            "violations": [],
            "count": 0
        }

# =============================
# Docstring & Type Hint Checks
# =============================
docstring_violations = []
type_hint_violations = []

try:
    with open("app.py", "r") as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not ast.get_docstring(node):
                docstring_violations.append(f"{node.name} missing docstring")
            if isinstance(node, ast.FunctionDef):
                for arg in node.args.args:
                    if arg.annotation is None:
                        type_hint_violations.append(f"{node.name} missing type hint for {arg.arg}")
                if node.returns is None:
                    type_hint_violations.append(f"{node.name} missing return type hint")
except FileNotFoundError:
    docstring_violations.append("app.py not found for analysis")

results["Docstring Check"] = {
    "status": "Passed" if not docstring_violations else "Failed",
    "violations": docstring_violations,
    "count": len(docstring_violations)
}

results["Type Hint Check"] = {
    "status": "Passed" if not type_hint_violations else "Failed",
    "violations": type_hint_violations,
    "count": len(type_hint_violations)
}

# =============================
# Dependency Analysis
# =============================
dependency_violations = []
try:
    with open("requirements.txt", "r") as f:
        deps = [line.strip() for line in f if line.strip()]
    if "requests" in deps and "httpx" in deps:
        dependency_violations.append("Redundant HTTP libraries: requests and httpx")
    if "flask" in deps and "flask_restful" in deps:
        dependency_violations.append("Redundant Flask libraries: flask and flask_restful")
except FileNotFoundError:
    dependency_violations.append("requirements.txt not found for dependency analysis")

results["Dependency Check"] = {
    "status": "Passed" if not dependency_violations else "Failed",
    "violations": dependency_violations,
    "count": len(dependency_violations)
}

# =============================
# Test Cases Pipeline
# =============================
test_results = []
test_folder = "./tests"

if os.path.exists(test_folder):
    for root, _, files in os.walk(test_folder):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                file_path = os.path.join(root, file)
                start_time = time.time()
                try:
                    # Run pytest for each file with timeout
                    process = subprocess.run(["pytest", file_path, "--timeout=3", "--disable-warnings"], capture_output=True, text=True)
                    elapsed = round(time.time() - start_time, 3)
                    status = "Passed" if process.returncode == 0 else "Failed"
                    test_results.append({
                        "file": file,
                        "status": status,
                        "elapsed_time": elapsed,
                        "log": process.stdout.strip()
                    })
                except Exception as e:
                    test_results.append({"file": file, "status": "Error", "error": str(e)})
else:
    test_results.append({"error": "No tests folder found"})

# Add to results dictionary
results["Test Cases Pipeline"] = {
    "status": "Passed" if all(r.get("status") == "Passed" for r in test_results if "status" in r) else "Failed",
    "violations": [json.dumps(r) for r in test_results],
    "count": len(test_results)
}

# =============================
# Print All Violations
# =============================
print("\nDocstring Violations:", docstring_violations)
print("Type Hint Violations:", type_hint_violations)
print("Dependency Violations:", dependency_violations)

# =============================
# Unified Summary Table
# =============================
summary_table = [[check, data["status"], data["count"], "\n".join(data["violations"])] for check, data in results.items()]

print("\nUnified Summary Report:")
print(tabulate(summary_table, headers=["Check Type", "Status", "Count", "Violations"], tablefmt="grid"))

# Save detailed report to JSON
with open("unified_summary_report.json", "w") as f:
    json.dump(results, f, indent=4)

print("\nDetailed report saved to unified_summary_report.json")

# =============================
# Client Checks
# =============================
client_results = {}

# Standard Coding Pipelines for client folder
client_checks = {
    "Client Type Check": ["mypy", "--ignore-missing-imports", "./client"],
    "Client Lint Check": ["flake8", "./client"],
    "Client Code Style Check": ["pycodestyle", "./client"],
    "Client Formatting Check": ["black", "--check", "./client"]
}

for check_name, command in client_checks.items():
    try:
        process = subprocess.run(command, capture_output=True, text=True)
        output = process.stdout.strip() + "\n" + process.stderr.strip()
        violations = []
        status = "Passed"
        if process.returncode != 0:
            status = "Failed"
            for line in output.split("\n"):
                if line.strip():
                    violations.append(line.strip())
        client_results[check_name] = {
            "status": status,
            "violations": violations,
            "count": len(violations)
        }
    except FileNotFoundError:
        client_results[check_name] = {
            "status": "Tool Not Installed",
            "violations": [],
            "count": 0
        }

# UI Test Pipeline (Mocha + Playwright)
ui_test_results = []
try:
    start_time = time.time()
    process = subprocess.run(["npm", "run", "test:mocha"], capture_output=True, text=True)
    elapsed = round(time.time() - start_time, 3)
    ui_test_results.append({
        "tool": "Mocha",
        "status": "Passed" if process.returncode == 0 else "Failed",
        "elapsed_time": elapsed,
        "log": process.stdout.strip()
    })

    start_time = time.time()
    process = subprocess.run(["npx", "playwright", "test"], capture_output=True, text=True)
    elapsed = round(time.time() - start_time, 3)
    ui_test_results.append({
        "tool": "Playwright",
        "status": "Passed" if process.returncode == 0 else "Failed",
        "elapsed_time": elapsed,
        "log": process.stdout.strip()
    })
except Exception as e:
    ui_test_results.append({"tool": "UI Tests", "status": "Error", "error": str(e)})

client_results["UI Test Pipeline"] = {
    "status": "Passed" if all(r.get("status") == "Passed" for r in ui_test_results) else "Failed",
    "violations": [json.dumps(r) for r in ui_test_results],
    "count": len(ui_test_results)
}

# Merge client results into main results
results.update(client_results)

from completion_summary import generate_summary
# Generate_summary report 
generate_summary(results)

# Exit code
sys.exit(exit_code)
