"""Private validation, index arithmetic, and coordinate helpers for H3D."""

from collections.abc import Iterator
from math import copysign, cos, floor, isfinite, radians, sin, sqrt
from numbers import Integral, Real

from h3.api import basic_int as _h3


# Index format and resolution constants.
_MAX_SURFACE_RESOLUTION = 15
# Format v1 freezes the binary64 result of sqrt(3.0) * H3_RES0_AVG_EDGE_M.
H3_RES0_AVG_EDGE_M = 1_281_256.011
BASE_THICKNESS_M = float.fromhex("0x1.0ee60411854c7p+21")
_FORMAT_VERSION = 1
_MAX_RESOLUTION = 10
_BASE_COUNT = 256
_VERSION_SHIFT = 60
_RESOLUTION_SHIFT = 56
_BASE_SHIFT = 48
_LOW_RESERVED_BITS = 18
_DIGIT_WIDTH = 3
_UNUSED_DIGIT = 7
_WORD_BITS = 64
_WORD_MASK = (1 << _WORD_BITS) - 1
_POWERS = tuple(7**r for r in range(_MAX_RESOLUTION + 1))
_VOXEL_MASK = (1 << (2 * _WORD_BITS)) - 1


# WGS84 conversion constants.
_A = 6_378_137.0
_F = 1 / 298.257223563
_E2 = _F * (2 - _F)
_B = _A * (1 - _F)
_MIN_CONVERSION_HEIGHT = -2_000_000.0
_MAX_CONVERSION_HEIGHT = 1_000_000_000.0
_MAX_RESIDUAL_M = 1e-5


# Input validation.

def _integer(value: object, name: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{name} must be an integer")
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be in [{minimum}, {maximum}]")
    return int(value)


def _finite(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")
    try:
        result = float(value)
    except OverflowError as error:
        raise ValueError(f"{name} must be finite in binary64") from error
    if not isfinite(result):
        raise ValueError(f"{name} must be finite in binary64")
    return result


def _canonical_latlng(lat: float, lng: float) -> tuple[float, float]:
    lat = _finite(lat, "latitude")
    lng = _finite(lng, "longitude")
    if not -90.0 <= lat <= 90.0:
        raise ValueError("latitude must be in [-90, 90] degrees")
    if not -180.0 <= lng <= 180.0:
        raise ValueError("longitude must be in [-180, 180] degrees")
    if abs(lat) == 90.0:
        return lat, 0.0
    return lat or 0.0, -180.0 if lng == 180.0 else lng or 0.0


# Vertical intervals and encoding.

def _boundary(ordinal: int, subdivisions: int) -> float:
    return BASE_THICKNESS_M * (ordinal / subdivisions - 0.5)


_MIN_ALTITUDE_M = _boundary(0, 1)
_MAX_ALTITUDE_M = _boundary(_BASE_COUNT, 1)


def _bounds(resolution: int, ordinal: int) -> tuple[float, float]:
    subdivisions = _POWERS[resolution]
    return _boundary(ordinal, subdivisions), _boundary(ordinal + 1, subdivisions)


def _midpoint(resolution: int, ordinal: int) -> float:
    subdivisions = _POWERS[resolution]
    return BASE_THICKNESS_M * ((2 * ordinal + 1 - subdivisions) / (2 * subdivisions))


def _decode_vertical(vertical: int) -> tuple[int, int]:
    word = _integer(vertical, "vertical word", 0, _WORD_MASK)
    if word >> _VERSION_SHIFT != _FORMAT_VERSION:
        raise ValueError("unsupported vertical version or nonzero high reserved bit")
    if word & ((1 << _LOW_RESERVED_BITS) - 1):
        raise ValueError("vertical low reserved bits must be zero")
    resolution = (word >> _RESOLUTION_SHIFT) & 15
    if resolution > _MAX_RESOLUTION:
        raise ValueError("unsupported vertical resolution")

    ordinal = (word >> _BASE_SHIFT) & (_BASE_COUNT - 1)
    digits = word >> _LOW_RESERVED_BITS
    for depth in range(_MAX_RESOLUTION):
        shift = _DIGIT_WIDTH * (_MAX_RESOLUTION - depth - 1)
        digit = (digits >> shift) & _UNUSED_DIGIT
        if depth < resolution:
            if digit == _UNUSED_DIGIT:
                raise ValueError("active vertical digits must be in [0, 6]")
            ordinal = 7 * ordinal + digit
        elif digit != _UNUSED_DIGIT:
            raise ValueError("unused vertical digits must be 7")
    return resolution, ordinal


def _encode_vertical(resolution: int, ordinal: int) -> int:
    unused_bits = _DIGIT_WIDTH * (_MAX_RESOLUTION - resolution)
    digits = (1 << unused_bits) - 1
    for shift in range(unused_bits, _DIGIT_WIDTH * _MAX_RESOLUTION, _DIGIT_WIDTH):
        ordinal, digit = divmod(ordinal, 7)
        digits |= digit << shift
    return (
        (_FORMAT_VERSION << _VERSION_SHIFT)
        | (resolution << _RESOLUTION_SHIFT)
        | (ordinal << _BASE_SHIFT)
        | (digits << _LOW_RESERVED_BITS)
    )


def _ordinal_at(altitude: float, subdivisions: int) -> int:
    ordinal = floor((altitude / BASE_THICKNESS_M + 0.5) * subdivisions)
    # The initial estimate can land on either side of a rounded boundary.
    # In particular, it can equal the count immediately below the global top.
    while altitude < _boundary(ordinal, subdivisions):
        ordinal -= 1
    while altitude >= _boundary(ordinal + 1, subdivisions):
        ordinal += 1
    return ordinal


# Voxel validation and encoding.

def _valid_cell(cell: int) -> int:
    cell = _integer(cell, "H3 cell", 0, _WORD_MASK)
    if not _h3.is_valid_cell(cell):
        raise ValueError("invalid H3 cell")
    return cell


def _voxel_parts(voxel: object) -> tuple[int, int, int, int]:
    voxel = _integer(voxel, "voxel", 0, _VOXEL_MASK)
    vertical = voxel >> _WORD_BITS
    resolution, ordinal = _decode_vertical(vertical)
    return _valid_cell(voxel & _WORD_MASK), vertical, resolution, ordinal


def _pack_voxel(cell: int, vertical: int) -> int:
    return (vertical << _WORD_BITS) | cell


# Hierarchy.

def _parent_resolution(value: int, resolution: int) -> int:
    return _integer(value, "parent vertical resolution", 0, resolution)


def _child_resolution(value: int, resolution: int) -> int:
    return _integer(value, "child vertical resolution", resolution, _MAX_RESOLUTION)


def _descendant_ordinals(
    resolution: int, ordinal: int, child_resolution: int
) -> range:
    scale = _POWERS[child_resolution - resolution]
    return range(ordinal * scale, (ordinal + 1) * scale)


def _voxel_descendants(
    cell: int, surface: int, target_surface: int, target_vertical: int, ordinals: range
) -> Iterator[int]:
    if target_surface == surface:
        cells = iter((cell,))
    else:
        count = _h3.cell_to_children_size(cell, target_surface)
        cells = (_h3.child_pos_to_cell(cell, target_surface, pos) for pos in range(count))
    for child in cells:
        for child_ordinal in ordinals:
            vertical = _encode_vertical(target_vertical, child_ordinal)
            yield _pack_voxel(child, vertical)


# Coordinate conversions.

def _conversion_height(altitude: float) -> float:
    if not _MIN_CONVERSION_HEIGHT <= altitude <= _MAX_CONVERSION_HEIGHT:
        raise ValueError("altitude is outside the supported WGS84 conversion envelope")
    return altitude


def _prime_vertical_radius(sin_lat: float) -> float:
    return _A / sqrt(1.0 - _E2 * sin_lat * sin_lat)


def _forward(lat: float, lng: float, alt: float) -> tuple[float, float, float]:
    if abs(lat) == 90.0:
        return 0.0, 0.0, copysign(_B + alt, lat)

    phi = radians(lat)
    sin_lat = sin(phi)
    radius = _prime_vertical_radius(sin_lat)
    p = (radius + alt) * cos(phi)
    z = (radius * (1.0 - _E2) + alt) * sin_lat
    if lng == -180.0:
        return -p, 0.0, z
    lam = radians(lng)
    return p * cos(lam), p * sin(lam), z
