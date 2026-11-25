"""Voxel validation, resolution inspection, and component access."""

from h3.api import basic_int as _h3

from ._core import _decode_vertical, _pack_voxel, _valid_cell, _voxel_parts


def is_valid_voxel(voxel: object) -> bool:
    """Return whether an object is a canonical H3D voxel integer.

    Parameters
    ----------
    voxel : object
        Value to check.

    Returns
    -------
    bool
        True if both words constitute a canonical voxel. Malformed inputs return False.
    """
    try:
        _voxel_parts(voxel)
    except (TypeError, ValueError):
        return False
    return True


def get_surface_resolution(voxel: int) -> int:
    """Return the resolution of the embedded H3 cell.

    Parameters
    ----------
    voxel : int
        Canonical 128-bit voxel ID.

    Returns
    -------
    int
        H3 surface resolution from 0 to 15.
    """
    cell, _, _, _ = _voxel_parts(voxel)
    return _h3.get_resolution(cell)


def get_vertical_resolution(voxel: int) -> int:
    """Return the resolution of the embedded vertical layer.

    Parameters
    ----------
    voxel : int
        Canonical 128-bit voxel ID.

    Returns
    -------
    int
        Vertical resolution from 0 to 10.
    """
    _, _, resolution, _ = _voxel_parts(voxel)
    return resolution


def voxel_to_h3(voxel: int) -> int:
    """Return the embedded H3 cell unchanged as an integer.

    Parameters
    ----------
    voxel : int
        Canonical 128-bit voxel ID.

    Returns
    -------
    int
        Original H3 cell.
    """
    cell, _, _, _ = _voxel_parts(voxel)
    return cell


def voxel_to_vertical(voxel: int) -> int:
    """Return the embedded vertical word unchanged as an integer.

    Parameters
    ----------
    voxel : int
        Canonical 128-bit voxel ID.

    Returns
    -------
    int
        Vertical word containing the layer and resolution.
    """
    _, vertical, _, _ = _voxel_parts(voxel)
    return vertical


def h3_to_voxel(cell: int, vertical: int) -> int:
    """Combine a valid H3 cell integer with a canonical vertical word.

    Parameters
    ----------
    cell : int
        Valid H3 cell integer.
    vertical : int
        Canonical 64-bit vertical word.

    Returns
    -------
    int
        Voxel ID containing the two words.
    """
    cell = _valid_cell(cell)
    _decode_vertical(vertical)
    return _pack_voxel(cell, int(vertical))


__all__ = [
    "is_valid_voxel",
    "get_surface_resolution",
    "get_vertical_resolution",
    "voxel_to_h3",
    "voxel_to_vertical",
    "h3_to_voxel",
]
