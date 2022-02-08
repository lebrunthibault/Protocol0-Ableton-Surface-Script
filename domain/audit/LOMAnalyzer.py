from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.shared.SongFacade import SongFacade


class LOMAnalyzer(object):
    """ Audit object model """
    def check_tracks_tree_consistency(self):
        # type: () -> None
        for simple_track in SongFacade.simple_tracks():
            # 1st layer checks
            if simple_track.group_track:
                assert simple_track in simple_track.group_track.sub_tracks, "failed on %s" % simple_track

            if simple_track.is_foldable:
                for sub_track in simple_track.sub_tracks:
                    assert sub_track.group_track == simple_track, "failed on %s" % simple_track

            # 2nd layer checks
            abstract_group_track = simple_track.abstract_group_track
            if simple_track.is_foldable:
                assert abstract_group_track.base_track == simple_track, "failed on %s" % simple_track
                assert len(abstract_group_track.sub_tracks) == len(simple_track.sub_tracks)
                for sub_track in abstract_group_track.sub_tracks:
                    if isinstance(sub_track, AbstractGroupTrack):
                        assert sub_track.group_track == abstract_group_track, "failed on %s" % simple_track
