import pytest
from playwright.sync_api import sync_playwright
import os
import csv
import logging
from collections import defaultdict
from datetime import datetime
from utils.common import CommonPage
from utils.mobile_common import MobileCommonPage
from locators.desktop_locator import LOCATORS_DESKTOP
from locators.mobile_locator import LOCATORS_MOBILE


logger = logging.getLogger(__name__)

def pytest_addoption(parser):
    parser.addini("desktop_base_url", "Desktop base URL for web tests", type="string")
    parser.addini("mobile_base_url", "Mobile base URL for mobile web tests", type="string")

@pytest.fixture(scope="session")
def desktop_base_url(request):
    return request.config.getini("desktop_base_url")

@pytest.fixture(scope="session")
def mobile_base_url(request):
    return request.config.getini("mobile_base_url")

@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p

def pytest_configure(config):
    config.option.timeout = 90

@pytest.fixture
def desktop_page(playwright_instance, request, desktop_base_url):
    channel = getattr(request, "param", "chrome")
    browser = playwright_instance.chromium.launch(channel=channel, headless=False)
    context = browser.new_context(base_url=desktop_base_url)
    page = context.new_page()
    meta = {
        "platform": "desktop",
        "channel": channel,
    }
    yield page, meta
    context.close()
    browser.close()

@pytest.fixture
def mobile_page(playwright_instance, request, mobile_base_url):
    device_name = getattr(request, "param", "iPhone 13 Pro")
    device = playwright_instance.devices[device_name]
    browser_type = device.get("default_browser_type", "webkit")
    browser = getattr(playwright_instance, browser_type).launch(headless=False)
    context = browser.new_context(**device, base_url=mobile_base_url)
    page = context.new_page()
    meta = {
        "platform": "mobile",
        "device": device_name,
    }
    yield page, meta
    context.close()
    browser.close()

@pytest.fixture
def common(request):
    # 데스크톱 테스트에서 사용하는 경우
    if "desktop_page" in request.fixturenames:
        page, meta = request.getfixturevalue("desktop_page")
        return CommonPage(page, LOCATORS_DESKTOP)
    # 모바일웹 테스트에서 사용하는 경우
    if "mobile_page" in request.fixturenames:
        page, meta = request.getfixturevalue("mobile_page")
        return CommonPage(page, LOCATORS_MOBILE)
    # 둘 다 없는 경우는 잘못 사용한 것
    raise RuntimeError("common fixture는 desktop_page 또는 mobile_page와 함께 사용해야 합니다.")

@pytest.fixture
def common_mobile(mobile_page):
    page, meta = mobile_page
    return MobileCommonPage(page, LOCATORS_MOBILE)

#! 별도 parametrize 없이 쓰면 기본 chrome + desktop_url 사용
@pytest.fixture
def page(desktop_page):
    page, _meta = desktop_page
    return page

def _take_failure_screenshot(item, page):
    os.makedirs("reports/defects", exist_ok=True)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_name = item.name.replace("[", "_").replace("]", "_")
    screenshot_file = f"reports/defects/{test_name}_{now}.png"
    page.screenshot(path=screenshot_file, full_page=True)
    logger.error(f"[DEFECT] Screenshot saved → {screenshot_file}")

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
        if rep.failed:
            page = None
            for key in ("desktop_page", "mobile_page", "page"):
                if key in item.funcargs:
                    page = item.funcargs[key]
                    if isinstance(page, tuple):
                        page = page[0]
                    break
            if page:
                _take_failure_screenshot(item, page)

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