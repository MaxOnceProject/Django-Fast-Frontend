"""
Tests for get_pagination ordering fix.

Ensures get_pagination applies order_by('pk') on unordered QuerySets to
eliminate UnorderedObjectListWarning from Django's Paginator.
"""

import pytest
from django.core.paginator import Page
from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock

from frontend.sites.model import ModelFrontend


class TestGetPaginationOrdering(TestCase):
    """get_pagination must apply order_by('pk') when the QuerySet is unordered."""

    def _make_mf(self):
        mf = ModelFrontend()
        mf.list_per_page = 100
        return mf

    def _get_request(self, params=None):
        return RequestFactory().get("/", params or {})

    def _mock_qs(self, ordered: bool):
        qs = MagicMock()
        qs.ordered = ordered
        child = MagicMock()
        child.count.return_value = 0
        child.__iter__ = MagicMock(return_value=iter([]))
        qs.order_by.return_value = child
        qs.count.return_value = 0
        qs.__iter__ = MagicMock(return_value=iter([]))
        return qs

    def test_unordered_queryset_is_sorted_by_pk(self):
        """When objects.ordered is False, order_by('pk') must be called."""
        mf = self._make_mf()
        mock_qs = self._mock_qs(ordered=False)

        mf.get_pagination(self._get_request(), mock_qs)

        mock_qs.order_by.assert_called_once_with("pk")

    def test_ordered_queryset_is_not_reordered(self):
        """When objects.ordered is True, order_by must NOT be called."""
        mf = self._make_mf()
        mock_qs = self._mock_qs(ordered=True)

        mf.get_pagination(self._get_request(), mock_qs)

        mock_qs.order_by.assert_not_called()

    def test_object_without_ordered_attr_passes_through(self):
        """Plain iterables with no .ordered attribute must not raise."""
        mf = self._make_mf()
        result = mf.get_pagination(self._get_request(), list(range(5)))
        self.assertIsNotNone(result)

    def test_pagination_returns_page_object(self):
        """get_pagination must return a Page, not the raw queryset."""
        mf = self._make_mf()
        result = mf.get_pagination(self._get_request(), list(range(10)))
        self.assertIsInstance(result, Page)

    def test_page_query_param_is_respected(self):
        """Passing ?page=2 must return the second page."""
        mf = self._make_mf()
        mf.list_per_page = 1
        request = self._get_request({"page": "2"})
        result = mf.get_pagination(request, [1, 2, 3])
        self.assertIsInstance(result, Page)
        self.assertEqual(result.number, 2)
