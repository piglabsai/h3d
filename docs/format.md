# Version 1 index format

A voxel is an unsigned 128-bit Python integer. Bits 63–0 are the complete H3 mode-1 cell. Bits 127–64 hold the vertical word. The table uses bit positions relative to that word.

| Bits | Width | Field |
| --- | ---: | --- |
| 63 | 1 | Reserved, zero |
| 62–60 | 3 | Format version, 1 |
| 59–56 | 4 | Vertical resolution, 0–10 |
| 55–48 | 8 | Base layer, 0–255 |
| 47–45 | 3 | Child digit 1 |
| 44–42 through 20–18 | 27 | Child digits 2–10, highest first |
| 17–0 | 18 | Reserved, zero |

At vertical resolution `r`, exactly the first `r` child digits are active and must be 0–6. Every remaining digit must be 7. The two words combine as `(vertical << 64) | cell`. A plain H3 cell on its own has no valid version-1 vertical word.

Use 32 lowercase hexadecimal digits for text interchange. In Python, use `format(voxel, "032x")` to write this representation and `int(text, 16)` followed by `is_valid_voxel()` to validate a parsed value. Use a string to preserve all bits in JSON. The packed integer sorts by the vertical resolution field before the layer fields, so altitude ordering across resolutions should use decoded heights or bounds.

For two-column storage, `voxel_to_parts()` returns `(h3_cell, vertical_word)`,
with the low word first. Both retain their original bits.
[DuckDB and Parquet storage example](usage.md#store-voxels-in-duckdb-and-parquet)

## Boundaries and hierarchy

The format freezes `B` at binary64 value `0x1.0ee60411854c7p+21` metres, approximately 2,219,200.508555028 m. It comes from `sqrt(3.0) * 1_281_256.011`, with the resolution-0 average H3 hexagon edge length frozen as a reference value. [H3 resolution statistics](https://h3geo.org/docs/core-library/restable/)

Start with ordinal `q` equal to the base-layer index. For each successive active digit, set `q = 7*q + digit`. Use `n = 7**r` at vertical resolution `r`. The canonical binary64 lower and upper endpoints are evaluated as `B * (q / n - 0.5)` and `B * ((q + 1) / n - 0.5)`, respectively. Use binary64 rounding after each operation in the written order. The lower endpoint is included, and the upper endpoint is excluded. The global endpoints use `q = 0` and `q = 256*n` in the lower endpoint expression.

The midpoint uses `B * ((2*q + 1 - n) / (2*n))`, with the numerator and denominator formed using exact integers. The parent ordinal is the child ordinal divided by `7**(child_resolution - parent_resolution)` using floor division.

## Known-answer vectors

These voxels use the resolution-0 H3 cell at latitude and longitude zero and are encoded at ellipsoidal height zero.

| Vertical resolution | Voxel hexadecimal |
| ---: | --- |
| 0 | `1000fffffffc000008075fffffffffff` |
| 1 | `11007ffffffc000008075fffffffffff` |
| 10 | `1a006db6db6c000008075fffffffffff` |

At vertical resolution 1, the canonical boundary at `B * (2 / 7 - 0.5)` belongs to vertical word `11005ffffffc0000`. The immediately preceding binary64 height belongs to `11003ffffffc0000`.

Changing the last digit of the vertical word in the first voxel to 1 makes a reserved bit nonzero. The resulting voxel `1000fffffffc000108075fffffffffff` is invalid.

Stored voxels carry their H3 cell directly. When generating an ID again from coordinates, the installed H3 version supplies the horizontal boundary decision.
