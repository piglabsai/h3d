# H3D — 3D Extension for Uber H3 Spatial Indexing

**Experimental preview.** Record the package version alongside persisted voxel
IDs while the API and index format are in early development.

**H3D extends [H3](https://h3geo.org/) into a three-dimensional,
Earth-referenced spatial index.** Each voxel combines an unchanged H3 cell with
a WGS84 ellipsoidal height interval in a single 128-bit identifier.

## Key capabilities

- **Three-dimensional indexing.** Assign terrestrial, atmospheric, or orbital
  positions to voxel IDs.
- **Independent resolutions.** Select H3 surface resolution 0–15 and vertical
  resolution 0–10 separately.
- **Hierarchical organization.** Aggregate positions into parent voxels or
  stream descendants and vertical ranges.
- **H3 interoperability.** Extract the original H3 cell for use with existing
  H3 data and tools.
- **Coordinate interfaces.** Index geodetic coordinates or Earth-centered,
  Earth-fixed Cartesian positions.

## Install

Install from PyPI with Python 3.10 or later.

```console
python -m pip install h3d
```

To install from a source checkout, run the following in its root.

```console
python -m pip install .
```

## First example

Find the voxel containing an ellipsoidal height of 75 m at latitude 52.52°
and longitude 13.405°.

```{doctest}
>>> import h3d
>>> voxel = h3d.latlngalt_to_voxel(
...     52.52, 13.405, 75.0, surface_resolution=9, vertical_resolution=8
... )
>>> h3d.get_surface_resolution(voxel), h3d.get_vertical_resolution(voxel)
(9, 8)
>>> lower, upper = h3d.voxel_altitude_bounds(voxel)
>>> lower <= 75.0 < upper
True
```

## The H3D grid

| Component | What it identifies |
| --- | --- |
| H3 cell | The horizontal footprint and its surface resolution |
| Vertical word | The ellipsoidal height interval and its vertical resolution |

The vertical grid has 256 base layers. Base layer 0 is centered on the WGS84
ellipsoid. Each refinement divides a layer into seven equal children. The
indexing domain extends from about 1,110 km below the ellipsoid to 567,006 km
above it. The lower endpoint is included and the upper endpoint is excluded.

Decoding returns the H3 grid center and the height interval midpoint. For
positions already expressed in Earth-fixed Cartesian metres, see
[Conversion functions](usage.md#conversion-functions).

## Documentation

- [Understand the grid](concepts.md) for voxel geometry and coordinate conventions.
- [Usage guide](usage.md) for runnable examples.
- [API quick reference](api_quick.md) for functions grouped by task.
- [API reference](api_reference.md) for public signatures and behavior.
- [Format specification](format.md) for encoding and boundary rules.
- [Contributor guide](https://github.com/piglabsai/h3d/blob/main/docs/contributing.md)
  for development setup, testing, and documentation builds.

```{toctree}
:hidden:
:caption: Using H3D

concepts
usage
api_quick
api_reference
```

```{toctree}
:hidden:
:caption: Technical details

format
```
