from itertools import islice
from math import inf, nextafter, sqrt
from random import Random

import pytest

import h3d

B = float.fromhex("0x1.0ee60411854c7p+21")
MINIMUM = -B / 2
MAXIMUM = 255.5 * B


def test_all_base_layers_are_adjacent_and_span_the_domain():
    assert B == sqrt(3.0) * 1_281_256.011
    layers = list(h3d.iter_vertical_range(MINIMUM, MAXIMUM, 0))
    assert len(layers) == 256
    previous_upper = MINIMUM
    for i, word in enumerate(layers):
        lower, upper = h3d.vertical_bounds(word)
        assert lower == previous_upper == (i - 0.5) * B
        assert upper == (i + 0.5) * B
        assert h3d.vertical_to_altitude(word) == i * B
        assert h3d.altitude_to_vertical(lower, 0) == word
        previous_upper = upper
    assert previous_upper == MAXIMUM


@pytest.mark.parametrize("base", [0, 255])
def test_child_digits_parent_relationship_and_coverage(base):
    parent = h3d.altitude_to_vertical(base * B, 0)
    for resolution in range(1, 11):
        children = list(h3d.vertical_to_children(parent, resolution))
        assert len(children) == 7
        assert [h3d.vertical_to_parent(word, resolution - 1) for word in children] == [parent] * 7
        assert [(word >> (48 - 3 * resolution)) & 7 for word in children] == list(range(7))
        bounds = [h3d.vertical_bounds(word) for word in children]
        assert (bounds[0][0], bounds[-1][1]) == h3d.vertical_bounds(parent)
        assert all(left[1] == right[0] for left, right in zip(bounds, bounds[1:]))
        for word, (lower, upper) in zip(children, bounds):
            assert upper - lower == pytest.approx(B / 7**resolution, abs=2e-7)
            assert h3d.altitude_to_vertical(lower, resolution) == word
            assert h3d.altitude_to_vertical(h3d.vertical_to_altitude(word), resolution) == word
        parent = children[3]
        if base == 0:
            assert h3d.vertical_to_altitude(parent).hex() == "0x0.0p+0"


@pytest.mark.parametrize("resolution", range(11))
def test_global_limits_and_floats_on_both_sides(resolution):
    first = h3d.altitude_to_vertical(MINIMUM, resolution)
    last = h3d.altitude_to_vertical(nextafter(MAXIMUM, -inf), resolution)
    assert h3d.vertical_bounds(first)[0] == MINIMUM
    assert h3d.altitude_to_vertical(nextafter(MINIMUM, inf), resolution) == first
    assert h3d.vertical_bounds(last)[1] == MAXIMUM
    for invalid in (nextafter(MINIMUM, -inf), MAXIMUM, nextafter(MAXIMUM, inf)):
        with pytest.raises(ValueError):
            h3d.altitude_to_vertical(invalid, resolution)


def test_boundary_correction_over_the_full_grid():
    rng = Random(413650)
    for resolution in range(11):
        n = 7**resolution
        count = 256 * n
        ordinals = [1, 255 * n, count - 1]
        if resolution:
            ordinals.extend((2, n // 2, n // 2 + 1))
        ordinals.extend(rng.sample(range(1, count), 128))
        for ordinal in ordinals:
            boundary = B * (ordinal / n - 0.5)
            below = h3d.altitude_to_vertical(nextafter(boundary, -inf), resolution)
            above = h3d.altitude_to_vertical(boundary, resolution)
            assert below != above
            assert h3d.vertical_bounds(below)[1] == boundary
            assert h3d.vertical_bounds(above)[0] == boundary
            assert h3d.altitude_to_vertical(nextafter(boundary, inf), resolution) == above
            assert list(h3d.iter_vertical_range(nextafter(boundary, -inf), boundary, resolution)) == [
                below
            ]


def test_range_intersection_and_lazy_full_domain():
    assert list(h3d.iter_vertical_range(MAXIMUM, MAXIMUM, 10)) == []
    assert list(h3d.iter_vertical_range(0.0, 0.0, 10)) == []
    assert list(h3d.iter_vertical_range(-0.005, 0.005, 10)) == [
        h3d.altitude_to_vertical(altitude, 10) for altitude in (-0.005, 0.0, 0.005)
    ]
    base_boundary = B / 2
    assert list(h3d.iter_vertical_range(base_boundary - 1, base_boundary + 1, 1)) == [
        h3d.altitude_to_vertical(base_boundary - 1, 1),
        h3d.altitude_to_vertical(base_boundary, 1),
    ]
    first = h3d.altitude_to_vertical(MINIMUM, 0)
    assert list(h3d.vertical_to_children(first, 0)) == [first]
    layers = h3d.iter_vertical_range(MINIMUM, MAXIMUM, 10)
    descendants = h3d.vertical_to_children(first, 10)
    assert list(islice(layers, 4)) == list(islice(descendants, 4))
