# Documentation guidelines

Use the same API categories and ordering in the quick and detailed references.
The categories are Indexing, Inspection, Traversal, Hierarchy, Conversion
functions, and Storage. Each category owns a Python module in `src/h3d/` and a
reference page in `docs/api/`. Define functions in their category module, list them in
its `__all__`, and re-export them from `h3d.__init__`. Put private helpers
and internal constants in `src/h3d/_core.py`. The quick reference uses Sphinx
summaries and each category page uses autodoc with the public `h3d` names.

Write public docstrings in NumPy style. Start with a short action summary,
then describe parameters, units, return values, and any function-specific
exceptions or numerical behavior. Use runnable examples in the usage guide
for tasks that span multiple functions.

Use *surface resolution* for the H3 level and *vertical resolution* for the
altitude level. Distinguish the vertical word, which encodes a layer, from the
height interval it represents. Call decoded values representative coordinates.
Geodetic positions use degrees and WGS84 ellipsoidal height in metres. ECEF
coordinates use metres.

Keep the README focused on installation and the first examples. Use the
concepts page for coordinate and hierarchy semantics, the usage guide for
runnable tasks, and the format specification for bit fields, boundary rules,
and known-answer vectors.
