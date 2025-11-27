import json
from pathlib import Path
import pytest
from loguru import logger
from pytest_check import check
from utils.mobile_common import MobileCommonPage 
from locators.mobile_locator import LOCATORS_MOBILE

@pytest.mark.mobile
@pytest.mark.parametrize("mobile_page", ["iPhone 13 Pro", "Pixel 5"], indirect=True)
def test_m_nav_list_texts_to_json(mobile_page):
    page, meta = mobile_page
    device = meta.get("device", "mobile")
    common = MobileCommonPage(page, logger=logger)
    logger.info(f"[MOBILE {device}] 네이버 모바일 메인 접속 (NAV_LIST 클릭 테스트)")
    visible = common.open_naver_mobile_and_prepare_nav()
    page.wait_for_timeout(2000)
    check.is_true(visible, "스크롤 후에도 NAV 화면이 나타나지 않음")
    output_path = f"reports/json/mobile_nav_list+_{device}.json"
    texts = common.nav_list_to_json(output_path)
    output_file = Path(output_path)
    check.is_true(output_file.exists(), "JSON 파일이 생성되지 않음")
    check.is_true(len(texts) > 0, "NAV_LIST 텍스트가 한 개도 추출되지 않음")