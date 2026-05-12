from __future__ import annotations

from typing import Any

from trends_brief.gather.base import GatherAdapter
from trends_brief.gather.http_json import HttpJsonAdapter
from trends_brief.gather.stub import StubAdapter

ADAPTERS: dict[str, type[GatherAdapter]] = {
    StubAdapter.name: StubAdapter,
    HttpJsonAdapter.name: HttpJsonAdapter,
}


def get_adapter(name: str) -> GatherAdapter:
    cls = ADAPTERS.get(name)
    if cls is None:
        raise KeyError(f"Unknown gather adapter: {name!r}. Known: {sorted(ADAPTERS)}")
    return cls()
