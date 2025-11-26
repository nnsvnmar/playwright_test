# locator 이름 앞을 무조건 DT 로 해 놔야 dict으로 자동으로 합쳐짐

DT_NAVER_HOME = {
    "search_box": "input#query",
    "search_button": "button#search_btn",
}

DT_NAVER_SEARCH_RESULT = {
    "google_link": "a:has-text('Google')",
}

DT_HOME_NOTIFY_ICON = {
    "notify_icon": "//*[@id='topNotiArea']/button",
}

LOCATORS_DESKTOP = {}
for name, value in list(globals().items()):
    if name.startswith("DT_") and isinstance(value, dict):
        LOCATORS_DESKTOP.update(value)