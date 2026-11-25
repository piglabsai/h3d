"""Split and restore voxel IDs for two-column integer storage."""

from ._core import _voxel_parts
from .inspection import h3_to_voxel as _h3_to_voxel


def voxel_to_parts(voxel: int) -> tuple[int, int]:
    """Split a voxel into its H3 cell and vertical word for storage.

    Parameters
    ----------
    voxel : int
        Canonical 128-bit voxel ID.

    Returns
    -------
    tuple[int, int]
        The original words in ``(h3_cell, vertical_word)`` order. Each is a
        Python integer that fits in an unsigned 64-bit column.
    """
    cell, vertical, _, _ = _voxel_parts(voxel)
    return cell, vertical


def parts_to_voxel(h3_cell: int, vertical_word: int) -> int:
    """Restore a voxel ID from its two unsigned 64-bit words.

    Parameters
    ----------
    h3_cell : int
        Valid H3 cell integer stored in the low word of the voxel.
    vertical_word : int
        Canonical vertical word stored in the high word of the voxel.

    Returns
    -------
    int
        Original 128-bit voxel ID as a Python integer.
    """
    return _h3_to_voxel(h3_cell, vertical_word)


__all__ = [
    "voxel_to_parts",
    "parts_to_voxel",
]
