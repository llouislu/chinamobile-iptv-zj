from pypinyin import lazy_pinyin, Style


class M3UWriter:
    def __init__(self, output_fo):
        self.output_fo = output_fo
        self._body = []
        self._parsed_channels = []
        self._extra_channels = []

    def write(self, channels):
        self._write_header()
        for name, livestream_url, index in channels:
            self._parsed_channels.append((name, livestream_url, index))
        # print(self._body)

    def save(self):
        self._extra_channels = sorted(self._extra_channels, key=lambda c: c[2])

        for index, (name, livestream_url, insert_index) in enumerate(self._extra_channels, 1):
            self._parsed_channels.insert(insert_index-1+index, (name, livestream_url, insert_index))

        for name, livestream_url, index in self._parsed_channels:
            self._write_channel(name, livestream_url)

        self.output_fo.writelines(self._body)

    def write_extras(self, extra_channels):
        for name, livestream_url, insert_index in extra_channels:
            self._extra_channels.append((name, livestream_url, insert_index))

    def __write_line(self, line):
        self._body.append(line)

    def _write_header(self):
        self.__write_line('#EXTM3U')
        self._write_empty_line()

    def _write_empty_line(self):
        self._body.append('\n\n')

    def _write_channel(self, name, livestream_url):
            pinyin_name = lazy_pinyin(name, style=Style.NORMAL)
            pinyin_name = ''.join(pinyin_name)
            self.__write_line('#EXTINF:-1 tvg-id="{pinyin_name}" group-title="CHINA MOBILE ZJ IPTV",{name}\n'.format(pinyin_name=pinyin_name, name=name))
            self.__write_line(livestream_url)
            self._write_empty_line()

def find_pattern(pattern, string):
    string = string.strip()
    previous, maybe_pattern, trailing = string.partition(pattern)
    if maybe_pattern == pattern:
        return True, trailing, previous
    return False, None, None

def read_dpl(dpl_file, parse_index=False):
    '''
    read daum playlist
    '''
    channel_livestream_pattern = '*file*'
    channel_name_pattern = '*title*'
    channels = []
    with open(dpl_file) as f:
        last_channel_livestream = ''
        last_channel_name = ''
        last_channel_index = -1

        for line in f:
            if last_channel_livestream:
                success, finding, _ = find_pattern(channel_name_pattern, line)
                if success:
                    last_channel_name = finding
                    channels.append([last_channel_name, last_channel_livestream, last_channel_index])
                    last_channel_livestream = ''
                    last_channel_index = -1
            else:
                success, finding, index = find_pattern(channel_livestream_pattern, line)
                if success:
                    last_channel_livestream = finding
                    last_channel_index = int(index)

    return channels

def write_m3u(channels, output_fo, extra_channels):
    m3u_writer = M3UWriter(output_fo)
    m3u_writer.write(channels)
    m3u_writer.write_extras(extra_channels)
    m3u_writer.save()

def filter_channels(filter, channels):
    channels

if __name__ == '__main__':
    import sys
    from pathlib import Path
    if len(sys.argv) < 2:
        exit('{} input.dpl [extra_channel_list]'.format(__file__))
    channels = read_dpl(sys.argv[1])
    with open('{}.m3u'.format(Path(sys.argv[1]).stem), 'w') as m3u_fo:
        extra_channels = []
        if len(sys.argv) >= 3:
            extras = read_dpl(sys.argv[2])
            extra_channels.extend(extras)
        write_m3u(channels, m3u_fo, extra_channels)


