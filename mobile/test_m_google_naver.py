from playwright.sync_api import sync_playwright
import pytest
import logging
from locator.locator_mobile import M_NAVER_HOME, M_NAVER_SEARCH_RESULT

logger = logging.getLogger(__name__)

@pytest.mark.mobile
@pytest.mark.parametrize("device", ["iPhone 13 Pro", "Pixel 5"])
def test_mobile_naver_search_google(device):
    logger.info(f"[MOBILE] ({device}) 네이버 검색 -> 구글 이동 테스트")
    with sync_playwright() as p:
        profile = p.devices[device]
        browser_type = profile.get("default_browser_type", "chromium")
        browser = getattr(p, browser_type).launch(headless=False)
        context = browser.new_context(**profile)
        page = context.new_page()
        logger.info(f"[MOBILE] ({device}) 네이버 메인 접속")
        page.goto("https://m.naver.com")
        search_trigger = page.locator(M_NAVER_HOME["search_trigger"])
        search_trigger.wait_for(state="visible")
        search_trigger.click()
        search_input = page.locator(M_NAVER_HOME["search_input"])
        search_input.wait_for(state="visible")
        search_input.fill("google")
        search_input.press("Enter")
        logger.info(f"[MOBILE] ({device}) 구글 검색")
        page.wait_for_load_state("networkidle")
        google_link = page.locator(M_NAVER_SEARCH_RESULT["google_link"]).first
        google_link.click()
        logger.info(f"[MOBILE] ({device}) 구글 링크 클릭")
        page.wait_for_load_state("load")
        title = page.title()
        logger.info(f"[MOBILE] ({device}) 현재 타이틀: {title}")
        assert "GOOGLE" in title.upper()
        logger.info(f"[MOBILE] ({device}) 구글 타이틀 검증 완료")
        context.close()
        browser.close()