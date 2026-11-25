import pytest

import h3d


def test_split_preserves_word_order_and_integer_types():
    voxel = 0x1A006DB6DB6C000008075FFFFFFFFFFF
    parts = h3d.voxel_to_parts(voxel)
    assert parts == (0x08075FFFFFFFFFFF, 0x1A006DB6DB6C0000)
    assert all(type(part) is int for part in parts)
    restored = h3d.parts_to_voxel(*parts)
    assert type(restored) is int
    assert restored == voxel


def test_storage_rejects_invalid_voxel_or_words():
    voxel = h3d.latlngalt_to_voxel(0, 0, 0, 0, 0)
    cell, vertical = h3d.voxel_to_parts(voxel)

    with pytest.raises(ValueError):
        h3d.voxel_to_parts(cell)
    with pytest.raises(TypeError):
        h3d.voxel_to_parts(True)
    with pytest.raises(ValueError):
        h3d.parts_to_voxel(vertical, cell)
    with pytest.raises(ValueError):
        h3d.parts_to_voxel(cell, vertical | 1)
    with pytest.raises(ValueError):
        h3d.parts_to_voxel(cell, 1 << 64)
    with pytest.raises(TypeError):
        h3d.parts_to_voxel(cell, True)


def test_duckdb_parquet_preserves_unsigned_words(tmp_path):
    duckdb = pytest.importorskip("duckdb")
    voxels = [
        h3d.latlngalt_to_voxel(52.52, 13.405, 75, 9, 8),
        h3d.latlngalt_to_voxel(52.52, 13.405, 565_000_000, 9, 10),
    ]
    path = str(tmp_path / "voxels.parquet")

    with duckdb.connect() as db:
        db.execute("""
            CREATE TABLE voxels (
                h3_cell UBIGINT NOT NULL,
                vertical_word UBIGINT NOT NULL
            )
        """)
        db.executemany("INSERT INTO voxels VALUES (?, ?)", [h3d.voxel_to_parts(v) for v in voxels])
        db.table("voxels").write_parquet(path)
        schema = db.execute(
            """
            SELECT name, converted_type
            FROM parquet_schema(?)
            WHERE name IN ('h3_cell', 'vertical_word')
            ORDER BY name
            """,
            [path],
        ).fetchall()
        rows = db.read_parquet(path).order("vertical_word").fetchall()

    assert schema == [("h3_cell", "UINT_64"), ("vertical_word", "UINT_64")]
    assert [h3d.parts_to_voxel(*row) for row in rows] == voxels
