"""Geodetic voxel indexing and vertical layer coordinates."""

from h3.api import basic_int as _h3

from ._core import (
    _MAX_ALTITUDE_M,
    _MAX_RESOLUTION,
    _MAX_SURFACE_RESOLUTION,
    _MIN_ALTITUDE_M,
    _POWERS,
    _bounds,
    _canonical_latlng,
    _decode_vertical,
    _encode_vertical,
    _finite,
    _integer,
    _midpoint,
    _ordinal_at,
    _pack_voxel,
    _voxel_parts,
)


def latlngalt_to_voxel(
    lat: float, lng: float, alt: float, surface_resolution: int, vertical_resolution: int
) -> int:
    """Encode latitude, longitude (degrees), and ellipsoidal height (metres).

    Parameters
    ----------
    lat : float
        WGS84 geodetic latitude in degrees, from −90 to +90.
    lng : float
        WGS84 longitude in degrees, from −180 to +180.
    alt : float
        WGS84 ellipsoidal height in metres.
    surface_resolution : int
        H3 surface resolution, from 0 to 15.
    vertical_resolution : int
        Vertical resolution, from 0 to 10.

    Returns
    -------
    int
        Voxel containing the input position.

    Notes
    -----
    The indexing domain includes the lower height bound and excludes the
    upper bound. Longitude is canonicalized at the antimeridian and poles.
    """
    lat, lng = _canonical_latlng(lat, lng)
    surface = _integer(surface_resolution, "surface resolution", 0, _MAX_SURFACE_RESOLUTION)
    vertical = altitude_to_vertical(alt, vertical_resolution)
    return _pack_voxel(_h3.latlng_to_cell(lat, lng, surface), vertical)


def voxel_to_latlngalt(voxel: int) -> tuple[float, float, float]:
    """Return the H3 grid center in degrees and the vertical midpoint in metres.

    Parameters
    ----------
    voxel : int
        Canonical 128-bit voxel ID.

    Returns
    -------
    tuple[float, float, float]
        Representative latitude, longitude, and ellipsoidal height.

    Notes
    -----
    Use the original surface and vertical resolutions to re-encode the
    representative point.
    """
    cell, _, resolution, ordinal = _voxel_parts(voxel)
    lat, lng = _canonical_latlng(*_h3.cell_to_latlng(cell))
    return lat, lng, _midpoint(resolution, ordinal)


def altitude_to_vertical(alt: float, vertical_resolution: int) -> int:
    """Encode ellipsoidal height in metres as a canonical 64-bit vertical word.

    Parameters
    ----------
    alt : float
        WGS84 ellipsoidal height in metres.
    vertical_resolution : int
        Vertical resolution, from 0 to 10.

    Returns
    -------
    int
        Vertical word for the layer containing the height.

    Notes
    -----
    The indexing domain includes the lower height bound and excludes the
    upper bound.
    """
    resolution = _integer(vertical_resolution, "vertical resolution", 0, _MAX_RESOLUTION)
    altitude = _finite(alt, "altitude")
    if not _MIN_ALTITUDE_M <= altitude < _MAX_ALTITUDE_M:
        raise ValueError("altitude is outside the H3D indexing domain")
    return _encode_vertical(resolution, _ordinal_at(altitude, _POWERS[resolution]))


def vertical_to_altitude(vertical: int) -> float:
    """Return the midpoint ellipsoidal height in metres of a vertical layer.

    Parameters
    ----------
    vertical : int
        Canonical 64-bit vertical word.

    Returns
    -------
    float
        Representative height of the layer.
    """
    return _midpoint(*_decode_vertical(vertical))


def vertical_bounds(vertical: int) -> tuple[float, float]:
    """Return the lower-inclusive and upper-exclusive heights in metres.

    Parameters
    ----------
    vertical : int
        Canonical 64-bit vertical word.

    Returns
    -------
    tuple[float, float]
        Bounds of the vertical layer.
    """
    return _bounds(*_decode_vertical(vertical))


def voxel_altitude_bounds(voxel: int) -> tuple[float, float]:
    """Return the voxel's lower-inclusive and upper-exclusive heights in metres.

    Parameters
    ----------
    voxel : int
        Canonical 128-bit voxel ID.

    Returns
    -------
    tuple[float, float]
        Lower and upper bounds of the embedded layer.
    """
    _, _, resolution, ordinal = _voxel_parts(voxel)
    return _bounds(resolution, ordinal)


__all__ = [
    "latlngalt_to_voxel",
    "voxel_to_latlngalt",
    "altitude_to_vertical",
    "vertical_to_altitude",
    "vertical_bounds",
    "voxel_altitude_bounds",
]
