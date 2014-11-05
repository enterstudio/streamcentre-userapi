# -*- coding: utf-8 -*-
from subprocess import Popen
import os
from userapiapp.help import convert_from_datetime
from cliptools.fragments_group import FragmentsGroup
from userapiapp.logger import get_logger

class Seamstress(object):
    def __init__(self, storage_proxy, temp_folder, result_folder, ffmpeg):
        self.temp_folder = temp_folder
        self.result_folder = result_folder
        self.ffmpeg = ffmpeg
        self.storage_proxy = storage_proxy


    def join_clip(self, fragments_to_join, output_file, cut_start=0, cut_length=None):
        converted = []
        for f in fragments_to_join:
            fragment_path = f[FragmentsGroup.DOWNLOAD_PATH_FIELD]
            new_filename = fragment_path + '.mpg'

            get_logger().debug("Convert %s to %s", fragment_path, new_filename)

            command = [self.ffmpeg,
                '-i', fragment_path,
                '-acodec', 'copy',
                '-vcodec', 'copy',
                '-f', 'mpegts',
                '-vbsf', 'h264_mp4toannexb',
                '-y',
                new_filename]
            Popen(command, bufsize=10**8).wait()
            converted.append(new_filename)

        all_clips = '|'.join(converted)

        get_logger().debug("Concat %d fragments to %s", len(converted), output_file)

        command = [self.ffmpeg,
                   '-i', 'concat:' + all_clips + '',
                   '-acodec', 'copy',
                   '-vcodec', 'copy',
                   '-ss', str(cut_start)]
        if cut_length: command += ['-t', str(cut_length)]
        command += ['-absf', 'aac_adtstoasc',
                    '-y',
                    output_file]

        print command

        Popen(command, bufsize=10**8).wait()

        for f in converted:
            get_logger().debug("Remove %s", f)
            os.remove(f)


    def compile_clip(self, stream_id, start, stop, request_id):
        start_stamp = convert_from_datetime(start)
        stop_stamp = convert_from_datetime(stop)
        info = self.storage_proxy.get_clips_info(stream_id, start_stamp, stop_stamp)
        sorted_clips = Seamstress.sort_clips(request_id, info['clips'])

        get_logger().debug("%d fragments for request %d found. %d groups",
            len(info['clips']), request_id, len(sorted_clips))

        output_files = []

        for group in sorted_clips:
            output_file = Seamstress.get_output_name(stream_id,
                group.start_stamp() + group.start_offset(start_stamp),
                group.length(start_stamp, stop_stamp))
            full_output_file = os.path.join(self.result_folder, output_file)

            if not os.path.isfile(full_output_file):
                group.download_fragments(self.storage_proxy, self.temp_folder)
                self.join_clip(group.fragments, full_output_file,
                    group.start_offset(start_stamp), group.length(start_stamp, stop_stamp))
                get_logger().info("Clip %s created", full_output_file)
            else:
                get_logger().info("Clip %s already exists", full_output_file)
            
            output_files.append(full_output_file)

            group.remove_downloaded()
            get_logger().debug("All fragments for request %d removed", request_id)

        return output_files


    @staticmethod
    def remove_fragments(clips_of_group):
        for f in clips_of_group:
            if os.path.isfile(f):
                os.remove(f)


    @staticmethod
    def sort_clips(request_id, all_clips, allowed_gap=1):
        s = sorted(all_clips, key=lambda clip: clip['start'])
        groups = []
        current_group = None
        for clip in s:
            if current_group and clip['start'] - current_group.stop_stamp() > allowed_gap:
                groups.append(current_group)
                current_group = None
            
            if not current_group:
                current_group = FragmentsGroup(request_id)
            current_group.add_fragment(clip)
        if current_group and current_group.fragments > 0:
            groups.append(current_group)
        return groups


    @staticmethod
    def get_output_name(stream_id, start, length):
        return "{0}_{1}_{2}.mp4".format(stream_id, float(start), float(start + length))


