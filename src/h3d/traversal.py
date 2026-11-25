"""Lazy traversal of vertical layers across a height range."""

from collections.abc import Iterator

from ._core import (
    _BASE_COUNT,
    _MAX_ALTITUDE_M,
    _MAX_RESOLUTION,
    _MIN_ALTITUDE_M,
    _POWERS,
    _boundary,
    _encode_vertical,
    _finite,
    _integer,
    _ordinal_at,
)


def iter_vertical_range(
    lower: float, upper: float, vertical_resolution: int
) -> Iterator[int]:
    """Lazily yield vertical layers intersecting the height interval [lower, upper).

    Parameters
    ----------
    lower : float
        Inclusive lower query height in metres.
    upper : float
        Exclusive upper query height in metres.
    vertical_resolution : int
        Vertical resolution, from 0 to 10.

    Returns
    -------
    Iterator[int]
        Intersecting vertical words in ascending altitude order.

    Notes
    -----
    Both query endpoints may coincide with the domain limits. Equal endpoints
    produce an empty iterator. Reversed or out-of-domain bounds raise ValueError.
    """
    resolution = _integer(vertical_resolution, "vertical resolution", 0, _MAX_RESOLUTION)
    lower = _finite(lower, "lower altitude")
    upper = _finite(upper, "upper altitude")
    if not _MIN_ALTITUDE_M <= lower <= upper <= _MAX_ALTITUDE_M:
        raise ValueError("range bounds must be ordered and within the indexing domain")
    if lower == upper:
        return iter(())

    subdivisions = _POWERS[resolution]
    start = _ordinal_at(lower, subdivisions)
    if upper == _MAX_ALTITUDE_M:
        stop = _BASE_COUNT * subdivisions
    else:
        stop = _ordinal_at(upper, subdivisions)
        if upper > _boundary(stop, subdivisions):
            stop += 1
    return (_encode_vertical(resolution, ordinal) for ordinal in range(start, stop))


__all__ = [
    "iter_vertical_range",
]
