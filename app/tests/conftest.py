import os
import re
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright


def _slugify_nodeid(nodeid):
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", nodeid).strip("-")


@pytest.fixture(scope="session")
def e2e_base_url():
    return os.environ.get("E2E_BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="session")
def screenshot_dir():
    path = Path(os.environ.get("PLAYWRIGHT_SCREENSHOT_DIR", "test-results/playwright"))
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture
def page(request, e2e_base_url, screenshot_dir):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(base_url=e2e_base_url)
        page = context.new_page()
        try:
            yield page
        finally:
            report = getattr(request.node, "rep_call", None)
            status = "passed" if report and report.passed else "failed"
            screenshot_path = screenshot_dir / f"{_slugify_nodeid(request.node.nodeid)}-{status}.png"
            try:
                page.screenshot(path=str(screenshot_path), full_page=True)
            finally:
                context.close()
                browser.close()