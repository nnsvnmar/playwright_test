import pytest
import logging
from locator.locator_desktop import DT_NAVER_HOME, DT_NAVER_SEARCH_RESULT

logger = logging.getLogger(__name__)

@pytest.mark.feature("naver-google search")
@pytest.mark.desktop
@pytest.mark.parametrize("channel", ["chrome", "msedge"])
def test_desktop_naver_search_google(channel, page):
    logger.info(f"[DESKTOP:{channel}] 네이버 검색 → 구글 이동 테스트 시작")
    page.goto("https://www.naver.com")
    logger.info("'google' 검색어 입력")
    search_box = page.locator(DT_NAVER_HOME["search_box"]).first
    search_box.click()
    search_box.fill("google")
    search_box.press("Enter")
    page.wait_for_load_state("networkidle")
    google_link = page.locator(DT_NAVER_SEARCH_RESULT["google_link"]).first
    google_link.click()
    page.wait_for_load_state("load")
    title = page.title()
    logger.info(f"현재 페이지 타이틀 확인: {title}")
    assert "GOOGLE" in title.upper()