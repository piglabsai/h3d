import h3d
from h3d import conversions, hierarchy, indexing, inspection, storage, traversal


def test_category_modules_own_and_export_the_public_api():
    exports = []
    for category in (indexing, inspection, traversal, hierarchy, conversions, storage):
        for name in category.__all__:
            function = getattr(category, name)
            assert function.__module__ == category.__name__
            assert getattr(h3d, name) is function
        exports.extend(category.__all__)

    assert exports == h3d.__all__
    assert len(exports) == len(set(exports))
