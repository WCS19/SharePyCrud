from typing import TypeVar, Callable, cast
import pytest

T = TypeVar("T")


def typed_fixture(func: Callable[..., T]) -> Callable[..., T]:
    return cast(Callable[..., T], pytest.fixture(func))
