from collections import defaultdict


class Track:
    def __init__(self, nodes, tracks):
        self.nodes = {}
        self.tracks = {}

        tracks_by_node = defaultdict(lambda: [])

        for node in nodes:
            self.nodes[node.uuid] = node

        for track in tracks:
            self.tracks[track.uuid] = track

            for node in track.get_nodes():
                tracks_by_node[node].append(track)

        for node in tracks_by_node:
            if node not in self.nodes:
                raise AssertionError(node + ' not found in provided nodes')
            if len(tracks_by_node[node]) != 2:
                print('Warning: node has ' + str(len(tracks_by_node[node])) + ' connections')

            for track in tracks_by_node[node]:
                for other_track in tracks_by_node[node]:
                    if track.uuid == other_track.uuid:
                        continue

                    track.add_connection(node, other_track)

    def get_updated_location(self, loc, offset):
        return self.tracks[loc.track_uuid].get_updated_location(loc, offset)

    def to_string(self):
        string = 'Track\n'
        string += '--- NODES ---\n\n'

        for n in self.nodes.values():
            string += n.to_string() + '\n'

        string += '\n--- TRACKS --- \n\n'

        for t in self.tracks.values():
            string += t.to_string()

        return string

    def render(self, render):
        for track in self.tracks.values():
            geom = track.get_geometry()
            render.attachNewNode(geom)
