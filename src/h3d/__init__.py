"""H3D — 3D Extension for Uber H3 Spatial Indexing."""

from .indexing import (
    latlngalt_to_voxel,
    voxel_to_latlngalt,
    altitude_to_vertical,
    vertical_to_altitude,
    vertical_bounds,
    voxel_altitude_bounds,
)
from .inspection import (
    is_valid_voxel,
    get_surface_resolution,
    get_vertical_resolution,
    voxel_to_h3,
    voxel_to_vertical,
    h3_to_voxel,
)
from .traversal import iter_vertical_range
from .hierarchy import (
    vertical_to_parent,
    vertical_to_children,
    voxel_to_parent,
    voxel_to_children,
)
from .conversions import (
    geodetic_to_ecef,
    ecef_to_geodetic,
    ecef_to_voxel,
    voxel_to_ecef,
)
from .storage import voxel_to_parts, parts_to_voxel

__all__ = [
    "latlngalt_to_voxel",
    "voxel_to_latlngalt",
    "altitude_to_vertical",
    "vertical_to_altitude",
    "vertical_bounds",
    "voxel_altitude_bounds",
    "is_valid_voxel",
    "get_surface_resolution",
    "get_vertical_resolution",
    "voxel_to_h3",
    "voxel_to_vertical",
    "h3_to_voxel",
    "iter_vertical_range",
    "vertical_to_parent",
    "vertical_to_children",
    "voxel_to_parent",
    "voxel_to_children",
    "geodetic_to_ecef",
    "ecef_to_geodetic",
    "ecef_to_voxel",
    "voxel_to_ecef",
    "voxel_to_parts",
    "parts_to_voxel",
]
