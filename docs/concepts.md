# Concepts and coordinate conventions

A voxel combines an H3 footprint with a height interval. At each latitude and longitude in that footprint, the height is measured along the WGS84 ellipsoid normal. The footprint can be an H3 hexagon or pentagon. Physical horizontal distances grow with altitude, and cell spacing varies with location.

H3D uses WGS84 geodetic latitude and longitude in degrees and ellipsoidal height in metres (EPSG:4979). Latitude ranges from −90° to +90°. Longitude ranges from −180° to +180° on input. H3D represents the antimeridian as −180° and sets longitude to zero at the exact poles. It passes the resulting angular coordinates directly to H3. Heights referenced to mean sea level or terrain, geocentric distances, and geocentric latitude require conversion before indexing.

The indexing domain is `[-1109600.254277514, 567005729.9358097)` metres. It spans part of Earth's subsurface and extends past the nominal distances of the Earth–Moon Lagrange points. Their Earth-fixed positions vary over time.

## Independent resolutions

The surface resolution is 0–15 and follows the H3 grid. The vertical resolution is 0–10. Vertical base layer 0 is centered on the ellipsoid. Each layer has seven equal children, numbered from low to high altitude. Layer thickness at vertical resolution `r` is nominally `B / 7**r`. It is about 7.856 mm at resolution 10.

Surface resolution `2*r` is a rough guide to matching horizontal and vertical spacing near the ellipsoid where the corresponding H3 resolution exists. H3D requires both resolutions explicitly and supports any valid pair.

Vertical ancestry gives exact containment under the format's boundary convention. Horizontal ancestry follows the H3 index hierarchy. Near horizontal cell edges, a logical parent can differ from the result of encoding the original position directly at that coarser H3 resolution. [H3 hierarchy](https://h3geo.org/docs/api/hierarchy/)

## Representative coordinates

Decoding returns the H3 grid center and the vertical midpoint. Keep the original resolution pair if you need to re-encode the representative point. For example, the central vertical descendant of base layer 0 has height exactly zero at every supported vertical resolution. Several distinct voxels with the same H3 cell therefore share representative coordinates. [H3 grid center](https://h3geo.org/docs/api/indexing/)

## Conversion functions

The standalone conversions use WGS84 ECEF (EPSG:4978). They support a height envelope of −2,000,000 to +1,000,000,000 metres, inclusive. The inverse applies that envelope to the recovered height and rejects unsupported points, including the Earth center. The voxel encoders both use the narrower half-open indexing domain.

Cartesian rounding can change which side of a boundary the recovered point lies on. Distinct geodetic inputs can produce identical ECEF inputs at binary64 precision. For example, at the equator the exact geodetic lower indexing bound and the immediately adjacent heights produce the same Cartesian position. Its recovered height is just below the bound, so the ECEF voxel encoder rejects it. The wrapper uses the recovered WGS84 position for indexing.
