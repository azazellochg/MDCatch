#!/usr/bin/env python3

""" This script parses BigTIFF file header and gets all the tags. """

import struct

file2 = '/home/gsharov/soft/application/acquisition_patterns/img_h1_s3_i534_movie_00001_Jul30_09.42.56.tif'
file = '/home/azazello/MEGA/application/acquisition_patterns/img_h1_s3_i534_movie_00001_Jul30_09.42.56.tif'
header_dict = dict()

with open(file, 'rb') as fin:
    fin.seek(0)
    header = fin.read(16)
    try:
        byteorder = {b'II': '<', b'MM': '>'}[header[:2]]
    except KeyError:
        print('Not a TIFF file!')

    version = struct.unpack(byteorder + 'H', header[2:4])[0]  # 43 = BigTIFF
    if version == 42:
        raise Exception('Only BigTIFF files are supported!')

    ifd_offset = struct.unpack(byteorder + 'Q', header[8:16])[0]  # offset to first IFD
    # find number of IFDs
    fin.seek(ifd_offset)
    num_ifds = struct.unpack(byteorder + 'Q', fin.read(8))[0]

    i = 1
    start = int(ifd_offset) + 8

    while i <= num_ifds:
        fin.seek(start)
        ifd = fin.read(20)
        tag = struct.unpack(byteorder + 'H', ifd[:2])[0]  # IFD tag
        dtype = struct.unpack(byteorder + 'H', ifd[2:4])[0]  # IFD type

        if dtype == 3 or dtype == 16:  # SHORT 2-byte uint / LONG8 8-byte uint
            header_dict[tag] = struct.unpack(byteorder + 'Q', ifd[12:20])[0]  # IFD value
        elif dtype == 5:  # RATIONAL 2x 4-byte uint
            header_dict[tag] = struct.unpack(byteorder + 'L', ifd[12:16])[0]
        elif dtype == 2:  # ASCII 8-byte
            count = struct.unpack(byteorder + 'Q', ifd[4:12])[0]
            offset = struct.unpack(byteorder + 'Q', ifd[12:20])[0]
            header_dict[tag] = (count, offset)
        elif dtype == 1:  # BYTE 1-byte uint
            header_dict[tag] = struct.unpack(byteorder + 'B', ifd[12:13])[0]
        i += 1
        start += 20

    # parse tags 270=ImageDescription, 306=DateTime & update dict
    for i in [270, 306]:
        count_desc, offset_desc = header_dict[i]
        fin.seek(offset_desc)
        part = fin.read(count_desc)
        res = struct.unpack(byteorder + '%ds' % count_desc,
                            part[:count_desc+1])[0]
        header_dict[i] = res.decode('utf-8').strip('\x00')

    for key in header_dict:
        print(key, "=", header_dict[key])
