from typing import Literal, Union, Mapping
from pathlib import Path
import json
from playwright.sync_api import Page, Locator

# 스크롤 후 화면 위치(상단, 중앙, 하단)
PositionType = Literal["top", "center", "bottom"]

class CommonPage:
    def __init__(self, page: Page, locators: Mapping[str, str] | None = None):
        self.page = page
        self.locators: dict[str, str] = dict(locators or {})

    # ---------- 내부 유틸 ----------
    def _get(self, key: str) -> str:
        locator = self.locators.get(key)
        if not locator:
            raise ValueError(f"[ERROR] Locator '{key}' not found in locators")
        return locator

    # ---------- 공통 함수 ----------
    def click(self, key: str):
        locator = self._get(key)
        self.page.locator(locator).click()

    # 반복 클릭
    def click_all(self, selector: str, delay_ms: int = 300):
        items = self.page.locator(selector)
        count = items.count()

        for i in range(count):
            items.nth(i).click()
            self.page.wait_for_timeout(delay_ms)

    def type_text(self, key: str, text: str, clear: bool = True, press_enter: bool = False):
        locator = self._get(key)
        field = self.page.locator(locator)
        field.wait_for(state="visible", timeout=5000)
        if clear:
            field.fill("")
        field.type(text)
        if press_enter:
            field.press("Enter")

    def get_text(self, key: str) -> str:
        locator = self._get(key)
        return self.page.locator(locator).inner_text().strip()

    def wait_for(self, key: str, timeout: int = 5000, state: str = "visible"):
        locator = self._get(key)
        self.page.locator(locator).wait_for(timeout=timeout, state=state)

    def is_visible(self, key: str) -> bool:
        locator = self._get(key)
        return self.page.locator(locator).is_visible()

    # ---------- 스크롤 관련 ----------
    def scroll_to_bottom(self, wait_ms: int = 1000) -> None:
        self.page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        self.page.wait_for_timeout(wait_ms)

    def scroll_by(self, delta_y: int, wait_ms: int = 300) -> None:
        self.page.evaluate(
            """(dy) => { window.scrollBy(0, dy); }""",
            delta_y,
        )
        self.page.wait_for_timeout(wait_ms)

    def align_element_in_viewport(
        self,
        target: Union[Locator, str],
        position: PositionType = "center",
        timeout: int = 5000,
    ) -> Locator:
        if isinstance(target, str):
            locator = self.page.locator(target)
        locator.wait_for(state="attached", timeout=timeout)
        block_map = {
            "top": "start",
            "center": "center",
            "bottom": "end",
        }
        block = block_map[position]
        locator.evaluate(
            """(el, block) => {
                el.scrollIntoView({
                    behavior: 'auto',
                    block,
                    inline: 'nearest',
                });
            }""",
            block,
        )
        return locator

    def align_in_viewport_by_key(
        self,
        key: str,
        position: PositionType = "center",
        timeout: int = 5000,
    ) -> Locator:
        locator_str = self._get(key)
        locator = self.page.locator(locator_str)
        return self.align_element_in_viewport(locator, position=position, timeout=timeout)

    # ---------- 텍스트 기반 스크롤 ----------
    def bring_text_into_view(
        self,
        text: str,
        position: PositionType = "center",
        exact: bool = True,
        timeout: int = 5000,
    ) -> Locator:
        if exact:
            locator = self.page.get_by_text(text, exact=True)
        else:
            locator = self.page.get_by_text(text)
        locator = self.page.get_by_text(text, exact=exact)
        locator = self.align_element_in_viewport(locator, position=position, timeout=timeout)
        locator.wait_for(state="visible", timeout=timeout)
        return locator

    def scroll_until_text(
        self,
        text: str,
        step: int | None = None,
        max_scroll: int = 30,
        exact: bool = False,
        wait_ms: int = 300,
    ) -> Locator:
        if step is None:
            step = self.page.evaluate("() => window.innerHeight")
        for _ in range(max_scroll):
            locator = self.page.get_by_text(text, exact=exact)
            if locator.count() > 0:
                return locator
            self.page.evaluate("(dy) => { window.scrollBy(0, dy); }", step)
            self.page.wait_for_timeout(wait_ms)
        raise Exception(f"Text '{text}' not found after scrolling {max_scroll} times.")

    # ---------- 팝업 / 토스트 처리 ----------

    def close_popup_if_visible(self, selector: str, timeout: int = 2000) -> bool:
        popup = self.page.locator(selector)
        try:
            popup.wait_for(state="visible", timeout=timeout)
        except Exception:
            return False
        popup.click()
        return True

    def wait_for_toast(
        self,
        selector: str,
        expected_text: str | None = None,
        timeout: int = 3000,
    ) -> str:
        toast = self.page.locator(selector)
        toast.wait_for(state="visible", timeout=timeout)
        text = toast.inner_text().strip()
        if expected_text is not None:
            # 여기서 pytest-check를 쓰고 싶으면 테스트 쪽에서 검사하는 걸 추천
            if expected_text not in text:
                raise AssertionError(f"토스트에 '{expected_text}' 가 없음: {text}")
        return text

    # ---------- 텍스트 JSON 저장 ----------
    def extract_texts_to_json(
        self,
        selector: str,
        output_path: str,
    ) -> None:
        loc = self.page.locator(selector)
        texts = [t.strip() for t in loc.all_text_contents()]
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(texts, f, ensure_ascii=False, indent=4)

    # ---------- selector 직접 사용하는 입력 (dict 안 쓰는 버전) ----------
    def type_text_direct(
        self,
        selector: str,
        text: str,
        clear: bool = True,
        press_enter: bool = False,
    ):
        field = self.page.locator(selector)
        field.wait_for(state="visible", timeout=5000)
        if clear:
            field.fill("")
        field.type(text)
        if press_enter:
            field.press("Enter")
