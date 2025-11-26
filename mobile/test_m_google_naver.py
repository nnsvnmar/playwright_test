from playwright.sync_api import sync_playwright
import pytest
import pytest_check as check
import logging
from locators.locator_mobile import LOCATORS_MOBILE

logger = logging.getLogger(__name__)

@pytest.mark.mobile
@pytest.mark.feature("mobile")
@pytest.mark.parametrize("mobile_page", ["iPhone 13 Pro", "Pixel 5"], indirect=True)
def test_mobile_naver_search_google(mobile_page, common):
    page, meta = mobile_page
    device = meta.get("device", "mobile")
    logger.info(f"[MOBILE] ({device}) 네이버 검색 → 구글 검색 결과 페이지 확인")
    logger.info(f"[MOBILE {device}] 네이버 모바일 메인 접속")
    page.goto("/", wait_until="domcontentloaded")
    common.wait_for("search_trigger")
    common.click("search_trigger")
    common.wait_for("search_input")
    logger.info(f"[MOBILE {device}] 'google' 검색어 입력")
    common.type_text("search_input", "google", clear=True, press_enter=True)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)
    url = page.url
    title = page.title()
    logger.info(f"[MOBILE {device}] 검색 결과 URL: {url}")
    logger.info(f"[MOBILE {device}] 검색 결과 타이틀: {title}")
    check.is_true(("search.naver.com" in url), "[MOBILE] 네이버 검색 결과 페이지로 이동하지 않음")
    check.is_in("google", url.lower(), "[MOBILE] URL에 google 검색어가 포함되어야 함")
    check.is_true("google" in title.lower(), "[MOBILE] 타이틀에 google 이 포함되어야 함")
    logger.info(f"[MOBILE {device}] 테스트 종료\n")
