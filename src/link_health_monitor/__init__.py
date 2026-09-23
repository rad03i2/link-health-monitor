"""Link Health Monitor public API."""

from .core import LinkResult, check_link, check_links, json_report, load_targets, summarize, validate_url

__version__ = "1.0.0"
__all__ = ["LinkResult", "check_link", "check_links", "json_report", "load_targets", "summarize", "validate_url"]
