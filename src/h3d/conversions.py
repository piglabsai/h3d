"""WGS84 geodetic and Earth-centered, Earth-fixed Cartesian conversions."""

from math import atan2, copysign, cos, degrees, hypot, sin, sqrt

from ._core import (
    _A,
    _B,
    _E2,
    _MAX_CONVERSION_HEIGHT,
    _MAX_RESIDUAL_M,
    _MIN_CONVERSION_HEIGHT,
    _canonical_latlng,
    _conversion_height,
    _finite,
    _forward,
    _prime_vertical_radius,
)
from .indexing import latlngalt_to_voxel as _latlngalt_to_voxel
from .indexing import voxel_to_latlngalt as _voxel_to_latlngalt


def geodetic_to_ecef(lat: float, lng: float, alt: float) -> tuple[float, float, float]:
    """Convert WGS84 geodetic coordinates to ECEF (x, y, z) in metres.

    Parameters
    ----------
    lat : float
        WGS84 geodetic latitude in degrees, from −90 to +90.
    lng : float
        WGS84 longitude in degrees, from −180 to +180.
    alt : float
        WGS84 ellipsoidal height in metres.

    Returns
    -------
    tuple[float, float, float]
        WGS84 ECEF coordinates (x, y, z).

    Notes
    -----
    The standalone conversion accepts heights from −2,000,000 to
    +1,000,000,000 metres. At an exact pole, x and y are zero.
    """
    lat, lng = _canonical_latlng(lat, lng)
    alt = _conversion_height(_finite(alt, "altitude"))
    return _forward(lat, lng, alt)


def ecef_to_geodetic(x: float, y: float, z: float) -> tuple[float, float, float]:
    """Convert ECEF metres to WGS84 latitude, longitude and ellipsoidal height.

    Parameters
    ----------
    x, y, z : float
        WGS84 ECEF coordinates in metres.

    Returns
    -------
    tuple[float, float, float]
        Latitude and longitude in degrees and recovered height in metres.

    Notes
    -----
    Recovered heights outside the conversion envelope raise ValueError.
    Longitude is zero on the polar axis.
    """
    x = _finite(x, "x")
    y = _finite(y, "y")
    z = _finite(z, "z")
    radius = hypot(x, y, z)
    # Each supported height lies on a normal offset of the ellipsoid. Its
    # distance from the origin lies between the polar and equatorial distances
    # of that offset. The residual allowance here guards only this precheck.
    if not (
        _B + _MIN_CONVERSION_HEIGHT - _MAX_RESIDUAL_M
        <= radius
        <= _A + _MAX_CONVERSION_HEIGHT + _MAX_RESIDUAL_M
    ):
        raise ValueError("ECEF point is outside the supported WGS84 conversion envelope")

    p = hypot(x, y)
    if p == 0.0:
        return copysign(90.0, z), 0.0, _conversion_height(abs(z) - _B)

    lng = degrees(atan2(y, x))
    if z == 0.0:
        lat, lng = _canonical_latlng(0.0, lng)
        return lat, lng, _conversion_height(p - _A)

    # Rearrange the forward equations to p*tan(phi) = z + e²*N*sin(phi).
    # This fixed-point map is a contraction in the supported height envelope.
    phi = atan2(z, p)
    for _ in range(16):
        sin_lat = sin(phi)
        next_phi = atan2(z + _E2 * _prime_vertical_radius(sin_lat) * sin_lat, p)
        if abs(next_phi - phi) <= 2e-16:
            phi = next_phi
            break
        phi = next_phi
    else:
        raise ValueError("ECEF latitude calculation did not converge")

    # Project onto the ellipsoid normal, avoiding division by a small cosine.
    sin_lat = sin(phi)
    alt = p * cos(phi) + z * sin_lat - _A * sqrt(1.0 - _E2 * sin_lat * sin_lat)
    alt = _conversion_height(alt)
    lat, lng = _canonical_latlng(degrees(phi), lng)
    rx, ry, rz = _forward(lat, lng, alt)
    if hypot(rx - x, ry - y, rz - z) > _MAX_RESIDUAL_M:
        raise ValueError("ECEF conversion failed the Cartesian residual check")
    return lat, lng, alt


def ecef_to_voxel(
    x: float, y: float, z: float, surface_resolution: int, vertical_resolution: int
) -> int:
    """Encode an ECEF point in metres using the specified voxel resolutions.

    Parameters
    ----------
    x, y, z : float
        WGS84 ECEF coordinates in metres.
    surface_resolution : int
        H3 surface resolution, from 0 to 15.
    vertical_resolution : int
        Vertical resolution, from 0 to 10.

    Returns
    -------
    int
        Voxel containing the recovered geodetic point.

    Notes
    -----
    The recovered height is indexed using the half-open domain. Cartesian
    rounding can change the result at a voxel boundary or domain endpoint.
    """
    return _latlngalt_to_voxel(*ecef_to_geodetic(x, y, z), surface_resolution, vertical_resolution)


def voxel_to_ecef(voxel: int) -> tuple[float, float, float]:
    """Return the voxel's representative ECEF coordinates in metres.

    Parameters
    ----------
    voxel : int
        Canonical 128-bit voxel ID.

    Returns
    -------
    tuple[float, float, float]
        WGS84 ECEF coordinates of the H3 grid center at the layer midpoint.
    """
    return geodetic_to_ecef(*_voxel_to_latlngalt(voxel))


__all__ = [
    "geodetic_to_ecef",
    "ecef_to_geodetic",
    "ecef_to_voxel",
    "voxel_to_ecef",
]
