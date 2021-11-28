.. OpenTimelineIO documentation master file, created by
   sphinx-quickstart on Sat Oct  9 10:02:05 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

OpenTimelineIO
==============

.. toctree::
   :hidden:

   architecture
   reference/index

OpenTimelineIO (OTIO) is an API and interchange format for editorial cut information. You can think
of it as a modern Edit Decision List (EDL) that also includes an API for reading, writing, and
manipulating editorial data. It also includes a plugin system for translating to/from existing
editorial formats as well as a plugin system for linking to proprietary media storage schemas.

OTIO supports clips, timing, tracks, transitions, markers, metadata, etc. but not embedded video or
audio. Video and audio media are referenced externally. We encourage 3rd party vendors, animation
studios and visual effects studios to work together as a community to provide adaptors for each
video editing tool and pipeline.
