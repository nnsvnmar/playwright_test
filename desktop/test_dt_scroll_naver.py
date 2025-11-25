# import logging
# import pytest
# from pytest_check import check
# from utils.common import scroll_to_bottom, bring_text_into_view, scroll_until_text, align_element_in_viewport
# from locators.locator_desktop import DT_NAVER_HOME

# logger = logging.getLogger(__name__)

# @pytest.mark.desktop
# def test_naver_scroll_to_bottom(desktop_page):
#     page, meta =desktop_page
#     channel = meta["channel"]
#     logger.info(f"[DESKTOP: {channel}] 네이버 메인 접속")
#     page.goto("/")
#     logger.info(f"[DESKTOP: {channel}] 네이버 메인 페이지 끝까지 스크롤")
#     scroll_to_bottom(page)
#     logger.info(f"[DESKTOP: {channel}] 네이버 메인 스크롤 끝인지 확인")
#     scroll_y = page.evaluate("() => window.scrollY")
#     doc_h = page.evaluate("() => document.documentElement.scrollHeight")
#     win_h = page.evaluate("() => window.innerHeight")
#     check.is_true(scroll_y + win_h >= doc_h - 50, "페이지 끝까지 내려가지 않음")

# @pytest.mark.desktop
# def test_naver_scroll_to_shopping_more(desktop_page):
#     page, meta = desktop_page
#     channel = meta["channel"]
#     logger.info(f"[DESKTOP: {channel}] 네이버 메인 접속")
#     page.goto("/")
#     target = bring_text_into_view(
#             page,
#             "카테크",
#             position="center",
#             exact=False
#     )
#     is_visible = target.is_visible()
#     logger.info(f"[DESKTOP: {channel}]'카테크' visible 여부: {is_visible}")
#     check.is_true(is_visible, "'쇼핑LIVE' 화면에 보이지 않음")
#     check.equal(is_visible, True, "'쇼핑LIVE' 화면에 보이지 않음")
#     scroll_until_text(target)

# @pytest.mark.desktop
# def test_naver_scroll_to_shopping_live(desktop_page):
#     page, meta = desktop_page
#     channel = meta["channel"]
#     logger.info(f"[{channel}] 네이버 메인 접속")
#     page.goto("/")
#     target = scroll_until_text(page, "쇼핑투데이")
#     logger.info("쇼핑투데이 발견됨, 화면 중앙으로 이동")
#     print(page.get_by_text("쇼핑", exact=False).all_text_contents())
#     align_element_in_viewport(target, position="center")
#     check.is_true(target.is_visible(), "'쇼핑투데이' 화면에 보이지 않음")