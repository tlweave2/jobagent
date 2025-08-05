"""
DOM utilities for monitoring page state.

This module provides helper functions to analyse and compare DOMs.
For example you might want to detect when the HTML of a page stops
changing significantly to decide that the page is stalled. This file
contains placeholder functions illustrating what such utilities could
look like.
"""
from __future__ import annotations

from typing import Optional


def has_stalled(previous_html: str, current_html: str, threshold: float = 0.05) -> bool:
    """Determine whether the DOM has stalled.

    Compares the lengths of two HTML strings. If the absolute
    difference in length divided by the length of the previous HTML
    is less than ``threshold`` the DOM is considered stalled.

    Args:
        previous_html: HTML string captured at the start of a monitoring period.
        current_html: HTML string captured at the end of the monitoring period.
        threshold: Fractional difference below which the DOM is considered
            unchanged.

    Returns:
        ``True`` if the DOM appears stalled, otherwise ``False``.
    """
    if not previous_html:
        return False
    prev_len = len(previous_html)
    curr_len = len(current_html)
    if prev_len == 0:
        return False
    delta = abs(curr_len - prev_len) / prev_len
    return delta < threshold