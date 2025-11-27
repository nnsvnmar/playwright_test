import json
from pathlib import Path
import pytest
from loguru import logger
from pytest_check import check
from locators.desktop_locator import LOCATORS_DESKTOP

@pytest.mark.desktop
def test_dt_search_with_common_actions(desktop_page, common):
    page, meta = desktop_page
    channel = meta["channel"]
    logger.info(f"[DESKTOP: {channel}] 네이버 메인 접속")
    page.goto("/", wait_until="domcontentloaded")
    common.wait_for("search_box")
    common.type_text("search_box", "Google", clear=True, press_enter=True)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)
    logger.info(f"[DESKTOP: {channel}] 검색 결과 URL: {page.url}")
    check.is_in("search.naver.com", page.url, "검색 결과 페이지로 이동하지 않음")
    logger.info(f"[DESKTOP: {channel}] 테스트 종료")

@pytest.mark.desktop
def test_dt_extract_texts_to_json(desktop_page, common):
    page, meta = desktop_page
    channel = meta["channel"]
    logger.info(f"[DESKTOP: {channel}] 네이버 메인 접속")
    page.goto("/", wait_until="domcontentloaded")
    page.wait_for_timeout(1000)
    selector="a"
    output_path="reports/json/desktop_naver_links.json"
    common.extract_texts_to_json(selector, output_path)
    output_file = Path(output_path)
    check.is_true(output_file.exists(), "JSON 파일이 생성되지 않음")
    data = json.loads(output_file.read_text(encoding="utf-8"))
    logger.info(f"[DESKTOP: {channel}] 추출된 텍스트 개수: {len(data)}")
    check.is_true(len(data) > 0, "텍스트가 한 개도 추출되지 않음")
    logger.info(f"[DESKTOP: {channel}] 테스트 종료")

@pytest.mark.desktop
def test_dt_notify_icon_click(desktop_page, common):
    page, meta = desktop_page
    channel = meta["channel"]
    logger.info(f"[DESKTOP: {channel}] 네이버 메인 접속")
    page.goto("/", wait_until="domcontentloaded")
    page.wait_for_timeout(1000)
    common.click("notify_icon")
    logger.info(f"[DESKTOP: {channel}] 아이콘 클릭 성공")
    logger.info(f"[DESKTOP: {channel}] 테스트 종료")

@pytest.mark.desktop
def test_dt_bring_text_into_view_stock(desktop_page, common):
    page, meta = desktop_page
    channel = meta["channel"]
    logger.info(f"[DESKTOP: {channel}] 네이버 메인 접속")
    page.goto("/", wait_until="domcontentloaded")
    target_text = "책방"
    logger.info(f"[DESKTOP: {channel}] '{target_text}' 텍스트 스크롤 탐색 시작")
    try:
        locator = common.bring_text_into_view(
            text=target_text,
            position="center",
            exact=False,
            timeout=5000
        )
    except Exception as e:
        logger.error(f"[DESKTOP: {channel}] bring_text_into_view 예외 발생: {e}")
        check.is_true(False, f"예외 발생: {e}")
        return
    visible = locator.is_visible()
    logger.info(f"[DESKTOP: {channel}] '{target_text}' 요소 노출 여부: {visible}")
    check.is_true(visible, f"'{target_text}' 텍스트가 화면에 보이지 않음")
    page.wait_for_timeout(800)
    logger.info(f"[DESKTOP: {channel}] bring_text_into_view 테스트 완료\n")