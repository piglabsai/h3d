from math import inf, nan, nextafter

import pytest
from h3.api import basic_int as h3

import h3d

CELL = 0x08075FFFFFFFFFFF
WORD = 0x1000FFFFFFFC0000
VOXEL = 0x1000FFFFFFFC000008075FFFFFFFFFFF


def test_known_answer_format_vectors():
    for resolution, expected in [
        (0, "1000fffffffc000008075fffffffffff"),
        (1, "11007ffffffc000008075fffffffffff"),
        (10, "1a006db6db6c000008075fffffffffff"),
    ]:
        value = h3d.latlngalt_to_voxel(0, 0, 0, 0, resolution)
        assert format(value, "032x") == expected
        assert h3d.voxel_to_h3(value) == CELL
        assert h3d.voxel_to_latlngalt(value)[2] == 0.0
    assert h3d.h3_to_voxel(CELL, WORD) == VOXEL
    assert h3d.voxel_to_vertical(VOXEL) == WORD
    boundary = float.fromhex("0x1.0ee60411854c7p+21") * (2 / 7 - 0.5)
    assert h3d.altitude_to_vertical(boundary, 1) == 0x11005FFFFFFC0000
    assert h3d.altitude_to_vertical(nextafter(boundary, -inf), 1) == 0x11003FFFFFFC0000


@pytest.mark.parametrize(
    "vertical",
    [
        -1,
        0,
        1 << 64,
        WORD | (1 << 63),
        WORD | (1 << 61),
        WORD | 1,
        WORD ^ (1 << 18),
        WORD | (1 << 56),
        WORD | (11 << 56),
    ],
)
def test_noncanonical_vertical_words_are_rejected(vertical):
    with pytest.raises(ValueError):
        h3d.h3_to_voxel(CELL, vertical)
    with pytest.raises(ValueError):
        h3d.vertical_bounds(vertical)
    assert not h3d.is_valid_voxel((vertical << 64) | CELL)


@pytest.mark.parametrize("voxel", [True, False, None, "1000fffffffc0000", 1.0, []])
def test_wrong_voxel_types(voxel):
    assert h3d.is_valid_voxel(voxel) is False
    with pytest.raises(TypeError):
        h3d.voxel_to_h3(voxel)


@pytest.mark.parametrize("value", [0, -1, CELL, WORD, 1 << 128, VOXEL | (1 << 128)])
def test_invalid_voxel_values(value):
    assert h3d.is_valid_voxel(value) is False
    with pytest.raises(ValueError):
        h3d.voxel_to_h3(value)
    with pytest.raises(ValueError):
        h3d.voxel_to_vertical(value)


def test_embedded_h3_cell_mode_and_word_size():
    edge = h3.origin_to_directed_edges(CELL)[0]
    vertex = h3.cell_to_vertex(CELL, 0)
    for cell in (0, edge, vertex, CELL | (1 << 63), CELL | (1 << 64)):
        with pytest.raises(ValueError):
            h3d.h3_to_voxel(cell, WORD)
        if cell < 1 << 64:
            assert not h3d.is_valid_voxel((WORD << 64) | cell)
    for value in (False, "8075fffffffffff", None, 2.0):
        with pytest.raises(TypeError):
            h3d.h3_to_voxel(value, WORD)
        with pytest.raises(TypeError):
            h3d.h3_to_voxel(CELL, value)


@pytest.mark.parametrize(
    ("args", "error"),
    [
        ((True, 0, 0, 0, 0), TypeError),
        ((0, "0", 0, 0, 0), TypeError),
        ((0, 0, complex(1, 1), 0, 0), TypeError),
        ((0, 0, 0, True, 0), TypeError),
        ((0, 0, 0, 0, False), TypeError),
        ((0, 0, 0, 0, 1.0), TypeError),
        ((91, 0, 0, 0, 0), ValueError),
        ((90, 181, 0, 0, 0), ValueError),
        ((nan, 0, 0, 0, 0), ValueError),
        ((0, inf, 0, 0, 0), ValueError),
        ((0, 0, -inf, 0, 0), ValueError),
        ((0, 0, 10**500, 0, 0), ValueError),
        ((0, 0, 0, 16, 0), ValueError),
        ((0, 0, 0, 0, -1), ValueError),
        ((0, 0, 0, 0, 11), ValueError),
    ],
)
def test_encode_validation(args, error):
    with pytest.raises(error):
        h3d.latlngalt_to_voxel(*args)


def test_invalid_requests_raise_at_iterator_creation():
    voxel = h3d.latlngalt_to_voxel(0, 0, 0, 3, 4)
    vertical = h3d.voxel_to_vertical(voxel)
    with pytest.raises(ValueError):
        h3d.voxel_to_children(voxel, 2, 4)
    with pytest.raises(TypeError):
        h3d.voxel_to_children(voxel, 3, True)
    with pytest.raises(ValueError):
        h3d.voxel_to_parent(voxel, 4, 4)
    with pytest.raises(ValueError):
        h3d.vertical_to_children(vertical, 3)
    with pytest.raises(ValueError):
        h3d.vertical_to_parent(vertical, 5)
    with pytest.raises(ValueError):
        h3d.iter_vertical_range(1, 0, 1)
    with pytest.raises(ValueError):
        h3d.iter_vertical_range(600_000_000, 600_000_000, 1)
    with pytest.raises(TypeError):
        h3d.iter_vertical_range(1, 2, False)


def test_conversion_invalid_types_and_unsupported_points():
    for xyz in [(0, 0, 0), (0, 0, 12_000), (inf, 0, 0), (2e9, 0, 0), (0, 10**500, 0)]:
        with pytest.raises(ValueError):
            h3d.ecef_to_geodetic(*xyz)
    with pytest.raises(ValueError):
        h3d.ecef_to_geodetic(0, 0, 1_006_370_000)
    with pytest.raises(TypeError):
        h3d.ecef_to_geodetic(False, 0, 1)
    with pytest.raises(ValueError):
        h3d.geodetic_to_ecef(0, 0, -2_000_001)
    with pytest.raises(ValueError):
        h3d.geodetic_to_ecef(0, 0, 1_000_000_001)
