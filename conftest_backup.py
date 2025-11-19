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

# 구역별 결과 집계용 전역 딕셔너리
FEATURE_RESULTS = defaultdict(lambda: {"passed": 0, "failed": 0})

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
    if rep.when == "call":
        feature_marker = item.get_closest_marker("feature")
        feature_name = feature_marker.args[0] if feature_marker else "UNSPECIFIED"

        if rep.failed:
            FEATURE_RESULTS[feature_name]["failed"] += 1
        elif rep.passed:
            FEATURE_RESULTS[feature_name]["passed"] += 1


# pytest 세션 종료 시 CSV 요약 파일 생성
#    - reports/test_summary_YYYYMMDD_HHMMSS.csv 형태로 저장
def pytest_sessionfinish(session, exitstatus):
    if not FEATURE_RESULTS:
        return
    os.makedirs("reports", exist_ok=True)
    now = datetime.now()
    ts_display = now.strftime("%Y-%m-%d %H:%M:%S")
    ts_file = now.strftime("%Y%m%d_%H%M%S")
    total_passed = sum(v["passed"] for v in FEATURE_RESULTS.values())
    total_failed = sum(v["failed"] for v in FEATURE_RESULTS.values())
    csv_path = os.path.join("reports", f"test_summary_{ts_file}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(
            [f"{ts_display} / Test Summary Passed : {total_passed}, Failed : {total_failed}"]
        )
        writer.writerow([])
        writer.writerow(["Feature", "Passed", "Failed"])
        for feature_name, result in sorted(FEATURE_RESULTS.items()):
            writer.writerow([
                feature_name,
                result["passed"],
                result["failed"],
            ])

    print(f"\n[REPORT] CSV summary saved: {csv_path}\n")