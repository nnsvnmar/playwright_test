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
    logger.info(f"[MOBILE] ({device}) 네이버 검색 -> 구글 이동 테스트")
    logger.info(f"[MOBILE] 네이버 메인 접속")
    page.goto("/")
    common.wait_for("search_trigger")
    common.click("search_trigger")
    common.wait_for("search_input")
    logger.info(f"[MOBILE {device}]: 구글 검색")
    common.type_text("search_input", "google", clear=True, press_enter=True)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)
    common.wait_for("google_link")
    logger.info(f"[MOBILE {device}]: 구글 링크 클릭")
    common.click("google_link")
    page.wait_for_load_state("load")
    page.wait_for_timeout(1000)
    title = page.title()
    logger.info(f"[MOBILE {device}]: 현재 타이틀 {title}")
    check.is_in("GOOGLE", title.upper(), f"[{device}] 타이틀에 GOOGLE이 포함되어야 함")
