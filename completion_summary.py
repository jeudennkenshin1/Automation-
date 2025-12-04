import json
import csv
from tabulate import tabulate

def generate_summary(results):
    # Short Form Summary
    print("\n=== Short Form Summary ===")
    for check, data in results.items():
        print(f"{check}: {data['status']} ({data['count']} issues)")

    # Unified Summary Table
    summary_table = [
        [check, data["status"], data["count"], "\n".join(data["violations"])]
        for check, data in results.items()
    ]
    print("\nUnified Summary Report:")
    print(tabulate(summary_table, headers=["Check Type", "Status", "Count", "Violations"], tablefmt="grid"))

    # Save JSON
    with open("unified_summary_report.json", "w") as f:
        json.dump(results, f, indent=4)

    # Save CSV
    with open("completion_summary.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Check Type", "Status", "Count", "Violations"])
        for check, data in results.items():
            writer.writerow([check, data["status"], data["count"], "; ".join(data["violations"])])