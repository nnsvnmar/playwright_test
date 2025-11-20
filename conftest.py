import pytest
from playwright.sync_api import sync_playwright
import os
import csv
from collections import defaultdict
from datetime import datetime

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()

GLOBAL_RESULTS = {"passed": 0, "failed": 0}
FEATURE_RESULTS = defaultdict(lambda: {"passed": 0, "failed": 0})
TESTCASE_RESULTS = defaultdict(lambda: {"passed": 0, "failed": 0})

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    if rep.when == "call":
        if rep.failed:
            GLOBAL_RESULTS["failed"] += 1
        elif rep.passed:
            GLOBAL_RESULTS["passed"] += 1
        feature_marker = item.get_closest_marker("feature")
        if feature_marker:
            feature_name = feature_marker.args[0]
            if rep.failed:
                FEATURE_RESULTS[feature_name]["failed"] += 1
            elif rep.passed:
                FEATURE_RESULTS[feature_name]["passed"] += 1
        testcase_name = item.name
        if rep.failed:
            TESTCASE_RESULTS[testcase_name]["failed"] += 1
        elif rep.passed:
            TESTCASE_RESULTS[testcase_name]["passed"] += 1

def pytest_sessionfinish(session, exitstatus):
    total_count = GLOBAL_RESULTS["passed"] + GLOBAL_RESULTS["failed"]
    if total_count == 0:
        return
    os.makedirs("reports", exist_ok=True)
    now = datetime.now()
    ts_display = now.strftime("%Y-%m-%d %H:%M:%S")
    ts_file = now.strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join("reports", f"test_summary_{ts_file}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(
            [f"{ts_display} / Test Summary Passed : {GLOBAL_RESULTS['passed']}, Failed : {GLOBAL_RESULTS['failed']}"]
        )
        writer.writerow([])
        writer.writerow(["Feature", "Passed", "Failed"])
        writer.writerow([
            "ALL",
            GLOBAL_RESULTS["passed"],
            GLOBAL_RESULTS["failed"],
        ])
        for feature_name, result in sorted(FEATURE_RESULTS.items()):
            writer.writerow([
                feature_name,
                result["passed"],
                result["failed"],
            ])
        writer.writerow([])
        writer.writerow(["Testcase(Function)", "Passed", "Failed"])
        for testcase_name, result in sorted(TESTCASE_RESULTS.items()):
            writer.writerow([
                testcase_name,
                result["passed"],
                result["failed"],
            ])
    print(f"\n[REPORT] CSV summary saved: {csv_path}\n")