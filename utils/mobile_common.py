from __future__ import annotations
from pathlib import Path
from typing import List, Optional
from playwright.sync_api import Page, Locator
import json
from locators.mobile_locator import LOCATORS_MOBILE

class MobileCommonPage:
    def __init__(self, page: Page, locators: dict | None = None, logger=None):
        self.page = page
        self.locators = locators or {}
        self.logger = logger

    def scroll_until_nav_list_visible(
            self,
            max_scroll: int = 10,
            scroll_ratio: float = 0.6,
            delay_ms: int = 400,
    ) -> bool:
        logger = self.logger
        page = self.page
        if logger:
            logger.info(f"[MOBILE] NAV_LIST 가 보일 때까지 최대 {max_scroll}번 스크롤 시도")
        container = page.locator("nav_list_container")
        page.evaluate("window.scrollTo(0,0)")
        page.wait_for_timeout(200)
        for idx in range(max_scroll):
            if container.count() > 0 and container.is_visible():
                if logger:
                    logger.info(f"[MOBILE] NAV_LIST 가 스크롤 {idx} 회 만에 화면에 노출됨")
                return True
            page.evaluate(
                """
                (ratio) => {
                    const dy = Math.floor(window.innerHeight * ratio);
                    window.scrollBy(0, dy);
                }
                """,
                scroll_ratio,
            )
            if logger:
                logger.debug(f"[MOBILE] NAV_LIST 탐색을 위한 스크롤 수행: idx = {idx}")
        page.wait_for_timeout(delay_ms)
        visible = container.count() > 0 and container.is_visible()
        if logger:
            logger.warning(f"[MOBILE] NAV_LIST 노출 여부 최종 확인: {visible}")
        return visible

    def get_nav_list_items(self) -> Locator:
        return self.page.locator("nav_list_items")

    def collect_nav_list_texts(self) -> List[str]:
        items = self.get_nav_list_items()
        count = items.count()
        texts: List[str] = []
        for i in range(count):
            text = items.nth(i).inner_text().strip()
            texts.append(text)
        return texts

    def nav_list_to_json(
            self,
            output_path: str,
    ) -> List[str]:
        logger = self.logger
        texts = self.collect_nav_list_texts()
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(texts, f, ensure_ascii=False, indent=4)
        if logger:
            logger.info(
                f"[MOBILE] NAV_LIST 텍스트 {len(texts)} 개를 JSON으로 저장: {output_path}"
            )
        return texts

    def click_all_nav_list_items(
            self,
            skip_first: bool = True,
            click_first_last: bool = True,
            wait_after_click_ms: int = 800,
            wait_after_back_ms: int = 700,
    ) -> List[str]:
        page = self.page
        logger = self.logger
        items = self.get_nav_list_items()
        total = items.count()
        clicked: List[str] = []
        if logger:
            logger.info(f"[MOBILE] NAV_LIST 내 메뉴 개수 {total}")
        indices = list(range(total))
        if skip_first:
            indices = indices[1:]
            if click_first_last and total > 0:
                indices.append(0)
        for idx in indices:
            current_items = self.get_nav_list_items()
            item = current_items.nth(idx)
            text = item.inner_text().strip()
            clicked.append(text)
            if logger:
                logger.info(f"[MOBILE] NAV_LIST[{idx}] '{text}' 클릭")
            with page.expect_navigation(timeout=15000):
                item.click
            page.wait_for_timeout(wait_after_click_ms)
            if logger:
                logger.info(f"[MOBILE] '{text}' 클릭 후 URL: {page.url}")
            page.go_back()
            page.wait_for_timeout(wait_after_back_ms)
        return clicked

    def open_naver_mobile_and_prepare_nav(
            self,
            base_url: Optional[str] = None,
            pause_after_visible_ms: int = 0,
    ) -> bool:
        page = self.page
        logger = self.logger
        target_url = base_url or "https://m.naver.com"
        if logger:
            logger.info(f"[MOBILE] 네이버 모바일 메인 접속: {target_url}")
        page.goto(target_url, wait_until="load", timeout=60000)
        page.wait_for_timeout(700)
        if logger:
            logger.info("[MOBILE] NAV_LIST 나타날 때까지 스크롤 시도")
        visible = self.scroll_until_nav_list_visible()
        if visible and pause_after_visible_ms > 0:
            page.wait_for_timeout(pause_after_visible_ms)
        return visible