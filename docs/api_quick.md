# API quick reference

Functions are grouped by task. Follow a function link for its complete API contract.

## Indexing

Encode geodetic positions, decode voxel representatives, and work with vertical intervals.

```{eval-rst}
.. currentmodule:: h3d

.. autosummary::

   latlngalt_to_voxel
   voxel_to_latlngalt
   altitude_to_vertical
   vertical_to_altitude
   vertical_bounds
   voxel_altitude_bounds
```

## Inspection

Validate voxel IDs, inspect their resolutions, and read or combine their component words.

```{eval-rst}
.. currentmodule:: h3d

.. autosummary::

   is_valid_voxel
   get_surface_resolution
   get_vertical_resolution
   voxel_to_h3
   voxel_to_vertical
   h3_to_voxel
```

## Traversal

Find vertical layers intersecting an altitude range.

```{eval-rst}
.. currentmodule:: h3d

.. autosummary::

   iter_vertical_range
```

## Hierarchy

Change the surface resolution, vertical resolution, or both.

```{eval-rst}
.. currentmodule:: h3d

.. autosummary::

   vertical_to_parent
   vertical_to_children
   voxel_to_parent
   voxel_to_children
```

## Conversion functions

Convert between WGS84 geodetic and ECEF coordinates, or index ECEF points directly.

```{eval-rst}
.. currentmodule:: h3d

.. autosummary::

   geodetic_to_ecef
   ecef_to_geodetic
   ecef_to_voxel
   voxel_to_ecef
```

## Storage

Split a voxel into two unsigned 64-bit words or restore it from those words.

```{eval-rst}
.. currentmodule:: h3d

.. autosummary::

   voxel_to_parts
   parts_to_voxel
```
