# API reference

Import public functions from `h3d` or from the category modules listed below.
The [quick reference](api_quick.md) links directly to each function. See the
[usage guide](usage.md) for runnable examples.

Geodetic coordinates use latitude and longitude in degrees followed by
ellipsoidal height in metres. Earth-centered, Earth-fixed coordinates use
`(x, y, z)` in metres. Surface resolution is 0–15 and vertical resolution is
0–10.

Indexes and resolutions accept integral values and reject booleans. Coordinates
accept real numbers that convert to finite binary64 values and reject
booleans. Functions raise `TypeError` for unsupported types and `ValueError`
for invalid values. `is_valid_voxel()` returns `False` for invalid IDs.
Lazy functions validate arguments at call time and return single-pass
iterators.

```{toctree}
:maxdepth: 1

api/indexing
api/inspection
api/traversal
api/hierarchy
api/conversions
api/storage
```
