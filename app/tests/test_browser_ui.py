import os

import pytest


pytestmark = [pytest.mark.ui]

E2E_USERNAME = os.environ.get("E2E_USERNAME", "ui-user")
E2E_PASSWORD = os.environ.get("E2E_PASSWORD", "top_secret")


def login(page, e2e_base_url):
    page.goto(f"{e2e_base_url}/accounts/login/")
    page.get_by_label("Username").fill(E2E_USERNAME)
    page.get_by_label("Password").fill(E2E_PASSWORD)
    page.get_by_role("button", name="Login").click()
    page.wait_for_url(f"{e2e_base_url}/")


def get_card_texts(page):
    return [card.inner_text() for card in page.locator(".card").all()]


def test_login_navigation_and_logout(page, e2e_base_url):
    login(page, e2e_base_url)

    page.locator(".frontend-sidebar a[href='/app/author/']").click()

    expect_url = f"{e2e_base_url}/app/author/"
    page.wait_for_url(expect_url)
    assert page.get_by_role("heading", name="Authors").is_visible()

    page.get_by_label("Account").click()
    page.get_by_role("button", name="Logout").click()

    page.wait_for_url("**/accounts/login/**")
    assert page.get_by_label("Username").is_visible()


def test_list_search_and_sort(page, e2e_base_url):
    login(page, e2e_base_url)
    page.goto(f"{e2e_base_url}/app/author/")

    page.get_by_placeholder("Search").fill("Ada")
    page.get_by_role("button", name="Search").click()
    page.wait_for_url(f"{e2e_base_url}/app/author/?q=Ada")

    card_texts = get_card_texts(page)
    assert any("name: Ada" in card_text for card_text in card_texts)
    assert all("name: Grace" not in card_text for card_text in card_texts)

    page.goto(f"{e2e_base_url}/app/author/")
    page.get_by_role("button", name="Filter and Sort").click()
    page.get_by_role("button", name="Name Descending").click()
    page.wait_for_url(f"{e2e_base_url}/app/author/?s=-name")

    assert "name: Marie" in get_card_texts(page)[0]


def test_add_and_change_author(page, e2e_base_url):
    login(page, e2e_base_url)
    page.goto(f"{e2e_base_url}/app/author/")

    page.locator("a[href$='/table_add']").click()
    page.get_by_label("Name").fill("Katherine")
    page.get_by_label("Title").fill("Mx")
    page.get_by_role("button", name="Save").click()

    assert page.get_by_label("Name").is_visible()

    page.goto(f"{e2e_base_url}/app/author/")
    page.locator(".card").filter(has_text="Katherine").first.locator("a[href*='/table_change/']").click()
    page.get_by_label("Name").fill("Katherine Johnson")
    page.get_by_role("button", name="Save").click()

    page.goto(f"{e2e_base_url}/app/author/")
    assert any("name: Katherine Johnson" in card_text for card_text in get_card_texts(page))