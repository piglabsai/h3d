"""Parent and child operations for vertical layers and voxels."""

from collections.abc import Iterator

from h3.api import basic_int as _h3

from ._core import (
    _MAX_SURFACE_RESOLUTION,
    _POWERS,
    _child_resolution,
    _decode_vertical,
    _descendant_ordinals,
    _encode_vertical,
    _integer,
    _pack_voxel,
    _parent_resolution,
    _voxel_descendants,
    _voxel_parts,
)


def vertical_to_parent(vertical: int, parent_resolution: int) -> int:
    """Return the vertical ancestor at the requested resolution.

    Parameters
    ----------
    vertical : int
        Canonical 64-bit vertical word.
    parent_resolution : int
        Target vertical resolution, at most the current resolution.

    Returns
    -------
    int
        Vertical word at the target resolution.
    """
    resolution, ordinal = _decode_vertical(vertical)
    target = _parent_resolution(parent_resolution, resolution)
    return _encode_vertical(target, ordinal // _POWERS[resolution - target])


def vertical_to_children(vertical: int, child_resolution: int) -> Iterator[int]:
    """Return a lazy iterator of vertical descendants in ascending altitude order.

    Parameters
    ----------
    vertical : int
        Canonical 64-bit vertical word.
    child_resolution : int
        Target vertical resolution, at least the current resolution.

    Returns
    -------
    Iterator[int]
        Descendant vertical words.

    Notes
    -----
    Arguments are validated when called. An equal target resolution yields
    the original word once.
    """
    resolution, ordinal = _decode_vertical(vertical)
    target = _child_resolution(child_resolution, resolution)
    return (
        _encode_vertical(target, child)
        for child in _descendant_ordinals(resolution, ordinal, target)
    )


def voxel_to_parent(voxel: int, surface_resolution: int, vertical_resolution: int) -> int:
    """Return the ancestor at the requested surface and vertical resolutions.

    Parameters
    ----------
    voxel : int
        Canonical 128-bit voxel ID.
    surface_resolution : int
        Target H3 resolution, at most the current resolution.
    vertical_resolution : int
        Target vertical resolution, at most the current resolution.

    Returns
    -------
    int
        Voxel at the requested resolutions.

    Notes
    -----
    Equal target resolutions preserve the corresponding index. Horizontal
    ancestry follows the H3 index hierarchy.
    """
    cell, _, resolution, ordinal = _voxel_parts(voxel)
    surface = _h3.get_resolution(cell)
    target_surface = _integer(surface_resolution, "parent surface resolution", 0, surface)
    target_vertical = _parent_resolution(vertical_resolution, resolution)
    if target_surface < surface:
        cell = _h3.cell_to_parent(cell, target_surface)
    vertical = _encode_vertical(target_vertical, ordinal // _POWERS[resolution - target_vertical])
    return _pack_voxel(cell, vertical)


def voxel_to_children(
    voxel: int, surface_resolution: int, vertical_resolution: int
) -> Iterator[int]:
    """Yield descendants by H3 child position, then ascending altitude.

    Parameters
    ----------
    voxel : int
        Canonical 128-bit voxel ID.
    surface_resolution : int
        Target H3 resolution, at least the current resolution.
    vertical_resolution : int
        Target vertical resolution, at least the current resolution.

    Returns
    -------
    Iterator[int]
        Lazy iterator of voxel IDs.

    Notes
    -----
    Arguments are validated when called. If both target resolutions match
    the input, the iterator yields the original voxel once.
    """
    cell, _, resolution, ordinal = _voxel_parts(voxel)
    surface = _h3.get_resolution(cell)
    target_surface = _integer(
        surface_resolution, "child surface resolution", surface, _MAX_SURFACE_RESOLUTION
    )
    target_vertical = _child_resolution(vertical_resolution, resolution)
    ordinals = _descendant_ordinals(resolution, ordinal, target_vertical)

    return _voxel_descendants(cell, surface, target_surface, target_vertical, ordinals)


__all__ = [
    "vertical_to_parent",
    "vertical_to_children",
    "voxel_to_parent",
    "voxel_to_children",
]
