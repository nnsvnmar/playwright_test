import os
import pytest
from datetime import datetime
from playwright.sync_api import sync_playwright

# pytest 커맨드 옵션 정의
def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser: chrome / msedge / chromium (desktop 전용)",
    )
    parser.addoption(
        "--device",
        action="store",
        default="none",
        help="Mobile device: none / iphone13 / pixel5",
    )

# 테스트 결과 리포트 훅 (성공/실패 여부 저장)
def pytest_runtest_makereport(item, call):
    """
    각 테스트 단계(setup/call/teardown)의 결과를 item.rep_setup, item.rep_call, item.rep_teardown 에 저장
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

# 공통 Playwright Page fixture
@pytest.fixture()
def page(request):
    """
    - --browser / --device 옵션에 따라
      데스크탑(Chrome/Edge/Chromium) 또는
      모바일(iPhone 13 Pro / Pixel 5) 환경을 생성
    - 실패 시 스크린샷 + trace 저장
    """
    browser_opt = request.config.getoption("--browser")
    device_opt = request.config.getoption("--device")
    # 출력 폴더 준비
    os.makedirs("artifacts/screenshots", exist_ok=True)
    os.makedirs("artifacts/traces", exist_ok=True)
    with sync_playwright() as p:
        browser = None
        context = None
        # 모바일 모드 (device_opt != none)
        if device_opt != "none":
            if device_opt == "iphone13":
                device_name = "iPhone 13 Pro"
            elif device_opt == "pixel5":
                device_name = "Pixel 5"
            else:
                raise ValueError(f"Unknown device option: {device_opt}")
            profile = p.devices[device_name]
            browser_type = profile.get("default_browser_type", "chromium")
            browser = getattr(p, browser_type).launch(headless=False)
            context = browser.new_context(**profile)
            print(f"[PLAYWRIGHT] Launching MOBILE: {device_name} ({browser_type})")
        # 데스크탑 모드 (device_opt == none)
        else:
            if browser_opt == "chrome":
                browser = p.chromium.launch(channel="chrome", headless=False)
                context = browser.new_context(viewport={"width": 1280, "height": 720})
                print("[PLAYWRIGHT] Launching DESKTOP Chrome")
            elif browser_opt == "msedge":
                browser = p.chromium.launch(channel="msedge", headless=False)
                context = browser.new_context(viewport={"width": 1280, "height": 720})
                print("[PLAYWRIGHT] Launching DESKTOP Edge")
            else:
                browser = p.chromium.launch(headless=False)
                context = browser.new_context(viewport={"width": 1280, "height": 720})
                print("[PLAYWRIGHT] Launching DESKTOP Chromium(default)")
        page = context.new_page()
        # Trace 기록 시작 (전체 테스트 구간)
        context.tracing.start(
            screenshots=True,
            snapshots=True,
            sources=True,
        )
        # 훅에서 접근할 수 있게 item에 붙여두기
        request.node._pw_page = page
        request.node._pw_context = context
        request.node._pw_browser = browser
        # 테스트 실행
        yield page
        # teardown: 실패 시 스샷/trace 저장
        test_name = request.node.name.replace("/", "_").replace("::", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        failed = getattr(request.node, "rep_call", None) and request.node.rep_call.failed
        if failed:
            screenshot_path = os.path.join(
                "artifacts",
                "screenshots",
                f"{test_name}_{timestamp}.png",
            )
            try:
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"[PLAYWRIGHT] Screenshot saved: {screenshot_path}")
            except Exception as e:
                print(f"[PLAYWRIGHT] Screenshot failed: {e}")
            # trace 저장
            trace_path = os.path.join(
                "artifacts",
                "traces",
                f"{test_name}_{timestamp}.zip",
            )
            try:
                context.tracing.stop(path=trace_path)
                print(f"[PLAYWRIGHT] Trace saved: {trace_path}")
            except Exception as e:
                print(f"[PLAYWRIGHT] Trace stop failed: {e}")
        else:
            # 실패가 아니면 trace만 종료(파일 저장 X)
            try:
                context.tracing.stop()
            except Exception:
                pass
        context.close()
        browser.close()
