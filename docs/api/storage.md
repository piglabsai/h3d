# Storage

Split and restore voxel IDs using two unsigned 64-bit integer columns.
These functions are available from `h3d.storage` and from `h3d`.

For schemas and a round-trip example, see
[Store voxels in DuckDB and Parquet](../usage.md#store-voxels-in-duckdb-and-parquet).

For storage within DuckDB, a single signed `HUGEINT` column can hold any H3D
version-1 voxel ID exactly because the zero top bit keeps the ID within the
signed 128-bit integer range. A direct Parquet export in DuckDB 2.0.1 writes
`HUGEINT` as `DOUBLE`. Its 53 bits of significand precision can round away
the low bits of the voxel ID. Use two `UBIGINT` columns for an exact Parquet
round trip.
[DuckDB numeric types](https://duckdb.org/docs/current/sql/data_types/numeric) ·
[Binary64 precision](https://docs.python.org/3/tutorial/floatingpoint.html#representation-error)

```{eval-rst}
.. autofunction:: h3d.voxel_to_parts
```

```{eval-rst}
.. autofunction:: h3d.parts_to_voxel
```
