# import json
# from pathlib import Path
# import pytest
# from loguru import logger
# from pytest_check import check
# from utils.common import extract_texts_to_json

# @pytest.mark.desktop
# def test_naver_news_titles_to_json_web(desktop_page):
#     page, meta = desktop_page
#     channel = meta["channel"]
#     logger.info(f"[DESKTOP: {channel}] 네이버 뉴스 메인 접속")
#     page.goto("https://news.naver.com",
#               wait_until="domcontentloaded",
#               timeout=60000)
#     page.wait_for_timeout(2000)
#     selector = "a.sa_text_title, strong.sa_text_strong"
#     page.wait_for_selector(selector, timeout=10000)
#     output_path = "reports/json/web_naver_news_titles.json"
#     logger.info(f"[DESKTOP: {channel}] 뉴스 제목 텍스트를 JSON 으로 저장: {output_path}")
#     extract_texts_to_json(page, selector, output_path)
#     output_file = Path(output_path)
#     assert output_file.exists(), "JSON 파일이 생성되지 않음"
#     data = json.loads(output_file.read_text(encoding="utf-8"))
#     logger.info(f"[DESKTOP: {channel}] 추출된 텍스트 개수: {len(data)}")
#     check.is_true(len(data) > 0, "뉴스 제목이 한 개도 추출되지 않음")
