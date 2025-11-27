# test_naver_search_google.py
import pytest
from pytest_check import check
from playwright.sync_api import sync_playwright
from loguru import logger
from locators.desktop_locator import DT_NAVER_HOME, DT_NAVER_SEARCH_RESULT

@pytest.mark.desktop
@pytest.mark.feature("web")
@pytest.mark.parametrize("desktop_page", ["chrome", "msedge"], indirect=True)
def test_desktop_naver_search_google(desktop_page, common):
    page, meta = desktop_page
    channel = meta["channel"]
    logger.info(f"===== [{channel}] 네이버 검색 → 구글 이동 테스트 시작 =====")
    logger.info("네이버 메인 페이지 진입")
    page.goto("/", wait_until="domcontentloaded")
    logger.info("'google' 검색어 입력")
    common.wait_for("search_box")
    common.type_text("search_box", "google", clear=True, press_enter=True)
    logger.info("검색 결과 로딩 대기")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(500)
    url = page.url
    title = page.title()
    logger.info(f"[{channel}] 검색 결과 URL: {url}")
    logger.info(f"[{channel}] 검색 결과 타이틀: {title}")
    check.is_in("search.naver.com", url, "검색 결과 페이지로 이동하지 않음")
    check.is_true("google" in title.lower(), "타이틀에 google이 포함되어야 함")
    logger.info(f"[{channel}] 테스트 종료\n")