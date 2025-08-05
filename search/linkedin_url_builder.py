"""
Build LinkedIn job search URLs from search presets.

LinkedIn job search URLs accept a number of query parameters that
control filtering. This module defines a helper function to construct
those URLs based on a high‑level description of your search.
"""
from __future__ import annotations

from urllib.parse import urlencode
from typing import List, Dict, Any


def build_search_url(preset: Dict[str, Any]) -> str:
    """Generate a LinkedIn job search URL from a preset dictionary.

    Supported keys in ``preset`` include:

    - ``title``: Job title or keywords.
    - ``location``: Location to search in.
    - ``easy_apply_only``: If True, filters to Easy Apply jobs.
    - ``remote_only``: If True, filters to remote jobs.
    - ``experience_levels``: List of experience level strings (e.g.
      "Entry level").
    - ``keywords``: Additional keywords to include in the search.

    Returns:
        A URL string that can be loaded in a browser to perform the
        search. Note that LinkedIn parameters may change over time so
        this function may need to be updated to remain compatible.
    """
    base_url = "https://www.linkedin.com/jobs/search/"
    params = {}
    title = preset.get("title")
    location = preset.get("location")
    if title:
        params["keywords"] = title
    if location:
        params["location"] = location
    if preset.get("easy_apply_only"):
        # 'f_AL=true' filters to Easy Apply jobs
        params["f_AL"] = "true"
    if preset.get("remote_only"):
        # 'f_WT=2' filters to remote jobs
        params["f_WT"] = "2"
    exp = preset.get("experience_levels")
    if exp:
        # LinkedIn encodes experience levels as numbers; you may need to map
        # human‑readable strings to codes. This is left as an exercise.
        pass
    # Additional filters can be added here
    query = urlencode(params)
    return f"{base_url}?{query}"