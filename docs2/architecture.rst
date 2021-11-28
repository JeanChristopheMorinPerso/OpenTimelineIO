Architecture
============

Canonical Structure
-------------------

Although you can compose your OTIO files differently if you wish, the canonical OTIO
structure is as follows:

* root: otio.schema.Timeline. This file contains information about the root of a timeline, including a global start offset, and a top level container, .tracks
* timeline.tracks: This member is a otio.schema.Stack which contains otio.schema.Track objects
* timeline.tracks[i]: The otio.schema.Track contained by a timeline.tracks contain the clips, transitions and subcontainers that compose the rest of the editorial data.
