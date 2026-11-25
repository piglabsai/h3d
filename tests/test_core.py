from itertools import islice
from random import Random

import pytest
from h3.api import basic_int as h3

import h3d

MINIMUM = -1_109_600.254277514
MAXIMUM = 567_005_729.9358097


@pytest.mark.parametrize("surface", range(16))
@pytest.mark.parametrize("vertical", range(11))
def test_all_resolution_pairs_round_trip_representatives(surface, vertical):
    pentagon = h3.get_pentagons(surface)[0]
    coordinates = (
        (0, 0, 0),
        (52.52, 13.405, 35),
        (-34.60, -58.38, -200),
        (0, -180, 384_400_000),
        (90, 0, 550_000_000),
        (-90, 0, MINIMUM),
        (*h3.cell_to_latlng(pentagon), 40_000),
    )
    for lat, lng, alt in coordinates:
        voxel = h3d.latlngalt_to_voxel(lat, lng, alt, surface, vertical)
        assert h3d.is_valid_voxel(voxel)
        assert h3d.get_surface_resolution(voxel) == surface
        assert h3d.get_vertical_resolution(voxel) == vertical
        assert h3d.voxel_to_h3(voxel) == h3.latlng_to_cell(lat, lng, surface)
        word = h3d.voxel_to_vertical(voxel)
        assert word == h3d.altitude_to_vertical(alt, vertical)
        assert h3d.voxel_altitude_bounds(voxel) == h3d.vertical_bounds(word)
        assert h3d.h3_to_voxel(h3d.voxel_to_h3(voxel), word) == voxel
        assert h3d.latlngalt_to_voxel(*h3d.voxel_to_latlngalt(voxel), surface, vertical) == voxel


@pytest.mark.parametrize("surface", range(16))
def test_poles_and_antimeridian_canonicalize(surface):
    for lat in (-90, 90):
        assert len({h3d.latlngalt_to_voxel(lat, lng, 0, surface, 10) for lng in (-180, -45, 180)}) == 1
    assert h3d.latlngalt_to_voxel(35, -180, 0, surface, 7) == h3d.latlngalt_to_voxel(
        35, 180, 0, surface, 7
    )


@pytest.mark.parametrize("is_pentagon", [False, True])
def test_combined_hierarchy_matches_independent_hierarchies(is_pentagon):
    cell = h3.get_pentagons(0)[0] if is_pentagon else h3.latlng_to_cell(0, 0, 0)
    word = h3d.altitude_to_vertical(100, 1)
    voxel = h3d.h3_to_voxel(cell, word)
    words = list(h3d.vertical_to_children(word, 2))
    cells = [h3.child_pos_to_cell(cell, 1, i) for i in range(h3.cell_to_children_size(cell, 1))]
    children = list(h3d.voxel_to_children(voxel, 1, 2))
    assert children == [h3d.h3_to_voxel(child, layer) for child in cells for layer in words]
    assert set(cells) == set(h3.cell_to_children(cell, 1))
    assert list(h3d.voxel_to_children(voxel, 0, 1)) == [voxel]
    for child in children:
        assert h3d.voxel_to_parent(child, 0, 1) == voxel
        assert h3d.voxel_to_h3(h3d.voxel_to_parent(child, 1, 1)) == h3d.voxel_to_h3(child)
        assert h3d.voxel_to_vertical(h3d.voxel_to_parent(child, 0, 2)) == h3d.voxel_to_vertical(child)
        assert h3d.voxel_to_parent(child, 1, 2) == child


def test_far_descendant_iteration_does_not_materialize_either_dimension(monkeypatch):
    def reject_materialization(*args):
        pytest.fail("full H3 child enumeration was called")

    monkeypatch.setattr(h3, "cell_to_children", reject_materialization)
    voxel = h3d.latlngalt_to_voxel(0, 0, 0, 0, 0)
    children = list(islice(h3d.voxel_to_children(voxel, 15, 10), 3))
    assert len(children) == 3
    assert len({h3d.voxel_to_h3(child) for child in children}) == 1
    assert [h3d.voxel_to_parent(child, 0, 0) for child in children] == [voxel] * 3


def test_random_coordinates_across_the_domain():
    rng = Random(890235)
    for horizontal_resolution in range(16):
        for vertical_resolution in range(11):
            for _ in range(12):
                lat, lng = rng.uniform(-90, 90), rng.uniform(-180, 180)
                alt = rng.uniform(MINIMUM, MAXIMUM)
                voxel = h3d.latlngalt_to_voxel(lat, lng, alt, horizontal_resolution, vertical_resolution)
                lower, upper = h3d.voxel_altitude_bounds(voxel)
                assert lower <= alt < upper
                assert h3d.voxel_to_h3(voxel) == h3.latlng_to_cell(lat, lng, horizontal_resolution)
                center = h3d.voxel_to_latlngalt(voxel)
                assert h3d.latlngalt_to_voxel(*center, horizontal_resolution, vertical_resolution) == voxel
