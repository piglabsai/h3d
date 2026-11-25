from decimal import Decimal, localcontext
from math import atan2, degrees, dist, inf, nextafter
from random import Random

import pytest

import h3d

MINIMUM = -1_109_600.254277514
MAXIMUM = 567_005_729.9358097
WGS84_A = 6_378_137.0
WGS84_B = 6_356_752.314245179
CARTESIAN_TOLERANCE_M = 1e-4
HEIGHT_TOLERANCE_M = 1e-6
ANGLE_TOLERANCE_DEG = 5e-12


def decimal_reference(height):
    """50-digit off-axis reference using rational sines and cosines."""
    with localcontext() as ctx:
        ctx.prec = 50
        a = Decimal("6378137")
        f = 1 / Decimal("298.257223563")
        sin_lat, cos_lat = Decimal(3) / 5, Decimal(4) / 5
        sin_lng, cos_lng = Decimal(12) / 13, Decimal(5) / 13
        e2 = f * (2 - f)
        normal = a / (1 - e2 * sin_lat**2).sqrt()
        h = Decimal.from_float(float(height))
        p = (normal + h) * cos_lat
        return float(p * cos_lng), float(p * sin_lng), float((normal * (1 - e2) + h) * sin_lat)


@pytest.mark.parametrize(
    "height",
    [MINIMUM, -900_000, -250, 0, 11_000, 400_000, 20_200_000, 35_786_000, 384_400_000, MAXIMUM],
)
def test_off_axis_reference(height):
    lat, lng = degrees(atan2(3, 4)), degrees(atan2(12, 5))
    xyz = decimal_reference(height)
    assert dist(h3d.geodetic_to_ecef(lat, lng, height), xyz) < CARTESIAN_TOLERANCE_M
    actual = h3d.ecef_to_geodetic(*xyz)
    assert actual[:2] == pytest.approx((lat, lng), abs=ANGLE_TOLERANCE_DEG, rel=0)
    assert actual[2] == pytest.approx(height, abs=HEIGHT_TOLERANCE_M, rel=0)
    assert dist(h3d.geodetic_to_ecef(*actual), xyz) < CARTESIAN_TOLERANCE_M


@pytest.mark.parametrize("height", [MINIMUM, 0, 35_786_000, MAXIMUM])
def test_equator_poles_and_antimeridian(height):
    equator = (WGS84_A + height, 0.0, 0.0)
    assert h3d.geodetic_to_ecef(0, 0, height) == equator
    assert h3d.ecef_to_geodetic(*equator) == pytest.approx(
        (0, 0, height), abs=HEIGHT_TOLERANCE_M, rel=0
    )
    anti = (-(WGS84_A + height), 0.0, 0.0)
    assert h3d.geodetic_to_ecef(0, 180, height) == h3d.geodetic_to_ecef(0, -180, height) == anti
    assert h3d.ecef_to_geodetic(anti[0], -0.0, 0.0)[1] == -180.0
    for pole in (-90, 90):
        z = (WGS84_B + height) if pole > 0 else -(WGS84_B + height)
        xyz = h3d.geodetic_to_ecef(pole, 120.0, height)
        assert xyz == (0.0, 0.0, z)
        assert h3d.ecef_to_geodetic(*xyz) == pytest.approx(
            (pole, 0, height), abs=HEIGHT_TOLERANCE_M, rel=0
        )


@pytest.mark.parametrize("latitude", [89.999999999, -89.999999999, nextafter(90.0, 0.0)])
@pytest.mark.parametrize("height", [MINIMUM, MAXIMUM])
def test_near_polar_axis(latitude, height):
    xyz = h3d.geodetic_to_ecef(latitude, 135.0, height)
    lat, lng, alt = h3d.ecef_to_geodetic(*xyz)
    assert lat == pytest.approx(latitude, abs=ANGLE_TOLERANCE_DEG, rel=0)
    assert lng == pytest.approx(135.0, abs=ANGLE_TOLERANCE_DEG, rel=0)
    assert alt == pytest.approx(height, abs=HEIGHT_TOLERANCE_M, rel=0)
    assert dist(h3d.geodetic_to_ecef(lat, lng, alt), xyz) < CARTESIAN_TOLERANCE_M


def test_ecef_encoding_uses_the_recovered_height_at_boundaries():
    heights = (nextafter(MINIMUM, -inf), MINIMUM, nextafter(MINIMUM, inf))
    points = {h3d.geodetic_to_ecef(0, 0, height) for height in heights}
    assert points == {(5_268_536.745722486, 0.0, 0.0)}
    point = points.pop()
    assert h3d.ecef_to_geodetic(*point)[2] == heights[0]
    assert h3d.is_valid_voxel(h3d.latlngalt_to_voxel(0, 0, MINIMUM, 15, 10))
    with pytest.raises(ValueError):
        h3d.ecef_to_voxel(*point, 15, 10)

    with pytest.raises(ValueError):
        h3d.ecef_to_voxel(*h3d.geodetic_to_ecef(0, 0, MAXIMUM), 4, 10)
    central = h3d.altitude_to_vertical(0, 10)
    exact_boundary = h3d.vertical_bounds(central)[1]
    for height in (exact_boundary - 1e-5, exact_boundary, exact_boundary + 1e-5):
        xyz = h3d.geodetic_to_ecef(32.4, 22.7, height)
        recovered = h3d.ecef_to_geodetic(*xyz)
        voxel = h3d.ecef_to_voxel(*xyz, 10, 10)
        assert voxel == h3d.latlngalt_to_voxel(*recovered, 10, 10)
        if height != exact_boundary:
            assert voxel == h3d.latlngalt_to_voxel(32.4, 22.7, height, 10, 10)


def test_random_conversion_and_indexing_at_all_resolutions():
    rng = Random(51542)
    for surface in range(16):
        for vertical in range(11):
            for lower, upper in ((MINIMUM + 1, 0), (0, MAXIMUM - 1)):
                lat, lng = rng.uniform(-90, 90), rng.uniform(-180, 180)
                alt = rng.uniform(lower, upper)
                xyz = h3d.geodetic_to_ecef(lat, lng, alt)
                geodetic = h3d.ecef_to_geodetic(*xyz)
                assert dist(h3d.geodetic_to_ecef(*geodetic), xyz) < CARTESIAN_TOLERANCE_M
                assert geodetic[2] == pytest.approx(alt, abs=HEIGHT_TOLERANCE_M, rel=0)
                voxel = h3d.latlngalt_to_voxel(lat, lng, alt, surface, vertical)
                assert h3d.ecef_to_voxel(*xyz, surface, vertical) == voxel
                center = h3d.voxel_to_ecef(voxel)
                assert center == h3d.geodetic_to_ecef(*h3d.voxel_to_latlngalt(voxel))
                assert h3d.ecef_to_voxel(*center, surface, vertical) == voxel
