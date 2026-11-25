# Usage guide

## Index a terrestrial position

Supply latitude and longitude in degrees and ellipsoidal height in metres.
Both resolution arguments are required.

```{doctest}
>>> import h3d
>>> voxel = h3d.latlngalt_to_voxel(
...     52.52, 13.405, 75.0, surface_resolution=9, vertical_resolution=8
... )
>>> lower, upper = h3d.voxel_altitude_bounds(voxel)
>>> lower <= 75.0 < upper
True
>>> h3d.voxel_to_h3(voxel) == voxel & ((1 << 64) - 1)
True
```

## Change resolution

Coarsen the two dimensions independently. Here the H3 footprint stays the
same while the height interval becomes coarser.

```{doctest}
>>> parent = h3d.voxel_to_parent(voxel, surface_resolution=9, vertical_resolution=7)
>>> h3d.voxel_to_h3(parent) == h3d.voxel_to_h3(voxel)
True
>>> voxel in h3d.voxel_to_children(parent, surface_resolution=9, vertical_resolution=8)
True
```

## Find layers in a height range

Iterate layers intersecting a half-open height interval. The returned words
are ordered from lowest to highest altitude.

```{doctest}
>>> layers = h3d.iter_vertical_range(-0.005, 0.005, vertical_resolution=10)
>>> [round(h3d.vertical_to_altitude(layer), 6) for layer in layers]
[-0.007856, 0.0, 0.007856]
```

## Conversion functions

Index a satellite position given in WGS84 ECEF metres. This example uses a
point on the Earth-fixed equatorial X axis 400 km above the ellipsoid.
Transform inertial positions using the observation time before indexing them.

```{doctest}
>>> satellite = h3d.ecef_to_voxel(
...     6_778_137.0, 0.0, 0.0, surface_resolution=5, vertical_resolution=4
... )
>>> lower, upper = h3d.voxel_altitude_bounds(satellite)
>>> lower <= 400_000.0 < upper
True
>>> xyz = h3d.voxel_to_ecef(satellite)
>>> h3d.ecef_to_voxel(*xyz, 5, 4) == satellite
True
```

`voxel_to_ecef()` decodes the representative point. Keep the original
resolutions to re-encode it. See the
[conversion envelope and boundary rules](concepts.md#conversion-functions).

## Store a voxel ID

Format the integer as a 32-digit hexadecimal string for interchange and
validate it after parsing. Record the package version with persisted IDs.

```{doctest}
>>> text = format(voxel, "032x")
>>> len(text)
32
>>> parsed = int(text, 16)
>>> h3d.is_valid_voxel(parsed) and parsed == voxel
True
```

## Store voxels in DuckDB and Parquet

Use two `UBIGINT` columns named `h3_cell` and `vertical_word` in DuckDB.
In Parquet, both columns use the unsigned 64-bit logical type
`INT(64, false)` on physical `INT64` columns. Use the `h3_cell` column
directly for joins with data indexed at the same H3 resolution.
[DuckDB numeric types](https://duckdb.org/docs/current/sql/data_types/numeric) ·
[Parquet logical types](https://parquet.apache.org/docs/file-format/types/logicaltypes/)

```{doctest}
>>> h3_cell, vertical_word = h3d.voxel_to_parts(voxel)
>>> h3_cell == h3d.voxel_to_h3(voxel)
True
>>> h3d.parts_to_voxel(h3_cell, vertical_word) == voxel
True
```

The following example uses the separately installed `duckdb` Python package.
It writes a Parquet file and restores the exact ID from the two columns.

```python
import duckdb
import h3d

voxel = h3d.latlngalt_to_voxel(
    52.52, 13.405, 75.0, surface_resolution=9, vertical_resolution=8
)

with duckdb.connect() as db:
    db.execute("""
        CREATE TABLE voxels (
            h3_cell UBIGINT NOT NULL,
            vertical_word UBIGINT NOT NULL
        )
    """)
    db.execute("INSERT INTO voxels VALUES (?, ?)", h3d.voxel_to_parts(voxel))
    db.table("voxels").write_parquet("voxels.parquet")
    rows = db.read_parquet("voxels.parquet").fetchall()

assert [h3d.parts_to_voxel(*row) for row in rows] == [voxel]
```
