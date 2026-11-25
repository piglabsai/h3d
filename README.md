# H3D — 3D Extension for Uber H3 Spatial Indexing

**A voxel is a spatial region with an ID.** H3D extends an H3 cell through a
WGS84 ellipsoidal height interval. Use it to group positions by voxel, change
grid detail, or look up the original H3 footprint.

**Experimental preview.** Record the package version alongside persisted voxel
IDs while the API and index format are in early development.

## Install

Install with Python 3.10 or later. The H3 dependency is installed automatically.

```console
python -m pip install h3d
```

To install from a source checkout instead, run the following in its root.

```console
python -m pip install .
```

## First example

Pass geodetic latitude and longitude in degrees and ellipsoidal height in metres. The representative coordinates combine the H3 grid center with the layer midpoint.

```pycon
>>> import h3d
>>> voxel = h3d.latlngalt_to_voxel(52.52, 13.405, 75.0, 9, 8)
>>> lower, upper = h3d.voxel_altitude_bounds(voxel)
>>> lower <= 75.0 < upper
True
>>> h3d.get_surface_resolution(voxel), h3d.get_vertical_resolution(voxel)
(9, 8)
>>> h3d.voxel_to_h3(voxel) == voxel & ((1 << 64) - 1)
True

```

## Conversion functions

The conversion functions accept Earth-centered, Earth-fixed (ECEF) Cartesian coordinates in metres. This example indexes an illustrative position on the ECEF equatorial X axis about 400 km above the ellipsoid.

```pycon
>>> satellite = h3d.ecef_to_voxel(6_778_137.0, 0.0, 0.0, 5, 4)
>>> lower, upper = h3d.voxel_altitude_bounds(satellite)
>>> lower <= 400_000.0 < upper
True
>>> x, y, z = h3d.voxel_to_ecef(satellite)
>>> h3d.ecef_to_voxel(x, y, z, 5, 4) == satellite
True

```

The satellite input must already be in WGS84 ECEF. Positions in an inertial frame require a frame transformation using the observation time before indexing.

## What to know

- Geodetic inputs use degrees and WGS84 ellipsoidal height in metres. The
  indexing domain extends from about 1,110 km below the ellipsoid to 567,006 km
  above it, with an exclusive upper bound.
- `surface_resolution` selects horizontal detail (0–15).
  `vertical_resolution` selects layer thickness (0–10), with approximately
  7.856 mm thickness at level 10.
- Voxel IDs are 128-bit Python integers. Use 32 lowercase hexadecimal digits
  for text interchange and `voxel_to_h3()` to recover the original H3 cell.

## Documentation

- [Documentation home](https://github.com/piglabsai/h3d/blob/main/docs/index.md)
- [Understand the grid](https://github.com/piglabsai/h3d/blob/main/docs/concepts.md)
- [Usage guide](https://github.com/piglabsai/h3d/blob/main/docs/usage.md)
- [API quick reference](https://github.com/piglabsai/h3d/blob/main/docs/api_quick.md)
- [API reference](https://github.com/piglabsai/h3d/blob/main/docs/api_reference.md)
- [Format specification](https://github.com/piglabsai/h3d/blob/main/docs/format.md)
- [Contributor guide](https://github.com/piglabsai/h3d/blob/main/docs/contributing.md)

H3D is licensed under [Apache-2.0](https://github.com/piglabsai/h3d/blob/main/LICENSE).
