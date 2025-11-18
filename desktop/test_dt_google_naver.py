# test_naver_search_google.py
import pytest
from playwright.sync_api import sync_playwright
import logging
from locator.locator_desktop import DT_NAVER_HOME, DT_NAVER_SEARCH_RESULT

logger = logging.getLogger(__name__)

@pytest.mark.desktop
@pytest.mark.parametrize("channel", ["chrome", "msedge"])
def test_desktop_naver_search_google(channel):
    logger.info(f"===== [{channel}] 네이버 검색 → 구글 이동 테스트 시작 =====")
    with sync_playwright() as p:
        logger.info(f"[{channel}] 브라우저 실행")
        browser = p.chromium.launch(channel=channel, headless=False)
        page = browser.new_page()
        logger.info("네이버 메인 페이지 진입")
        page.goto("https://www.naver.com")
        logger.info("'google' 검색어 입력")
        search_box = page.locator(DT_NAVER_HOME["search_box"]).first
        search_box.click()
        search_box.fill("google")
        search_box.press("Enter")
        logger.info("검색 결과 로딩 대기")
        page.wait_for_load_state("networkidle")
        google_link = page.locator(DT_NAVER_SEARCH_RESULT["google_link"]).first
        google_link.click()
        page.wait_for_load_state("load")
        title = page.title()
        logger.info(f"현재 페이지 타이틀 확인: {title}")
        assert "GOOGLE" in title.upper()
        browser.close()
        logger.info(f"[{channel}] 테스트 종료\n")