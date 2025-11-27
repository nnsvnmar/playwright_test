# locator 이름 앞을 무조건 M 으로 해 놔야 dict으로 자동으로 합쳐짐

M_NAVER_HOME = {
    "search_trigger": "input#MM_SEARCH_FAKE",
    "search_input": "input#query",
}

M_NAVER_SEARCH_RESULT = {
    "google_link": "a:has-text('Google')",
}

M_NAVER_NAV_LIST = {
    "nav_list_container": "//*[@id='NAV_LIST']",
    "nav_list_items": "//*[@id='NAV_LIST']//li[contains(@class, 'nav_item')]//a",
}

LOCATORS_MOBILE = {}
for name, value in list(globals().items()):
    if name.startswith("M_") and isinstance(value, dict):
        LOCATORS_MOBILE.update(value)