# -*- coding: utf-8 -*-
import os

class FragmentsGroup(object):
    DOWNLOAD_PATH_FIELD = 'download_path'

    def __init__(self, request_id):
        self.fragments = []
        self.request_id = request_id

    def add_fragment(self, fragment):
        fragment[FragmentsGroup.DOWNLOAD_PATH_FIELD] = None
        self.fragments.append(fragment)

    def start_stamp(self):
        return self.fragments[0]['start'] if self.fragments else None

    def stop_stamp(self):
        return self.fragments[-1]['stop'] if self.fragments else None

    def start_offset(self, global_start):
        return global_start - self.start_stamp() if global_start > self.start_stamp() else 0

    def length(self, global_start, global_stop):
        result = self.stop_stamp() - self.start_stamp() - self.start_offset(global_start)
        if global_stop < self.stop_stamp():
            result -= self.stop_stamp() - global_stop
        return result

    def download_fragments(self, storage_proxy, temp_folder):
        for f in self.fragments:
            clip_id = f['clip_id']
            file_name = "{0}_{1}_fragment.avi".format(self.request_id, clip_id)
            f[FragmentsGroup.DOWNLOAD_PATH_FIELD] = os.path.join(temp_folder, file_name)
            storage_proxy.get_clip(f[FragmentsGroup.DOWNLOAD_PATH_FIELD], clip_id)

    def remove_downloaded(self):
        for f in self.fragments:
            path = f[FragmentsGroup.DOWNLOAD_PATH_FIELD]
            if path and os.path.isfile(path): os.remove(path)
            f[FragmentsGroup.DOWNLOAD_PATH_FIELD] = None
