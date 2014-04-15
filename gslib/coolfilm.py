
# what a really cool film!

import sys
import struct
import ctypes
import threading
import time

import pyglet.lib
from pyglet.compat import asbytes, asbytes_filename

if sys.platform.startswith('win') and struct.calcsize('P') == 8:
    av = 'avbin64'
else:
    av = 'avbin'

av = pyglet.lib.load_library(av)

AVBIN_RESULT_ERROR = -1
AVBIN_RESULT_OK = 0
AVbinResult = ctypes.c_int

AVBIN_STREAM_TYPE_UNKNOWN = 0
AVBIN_STREAM_TYPE_VIDEO = 1
AVBIN_STREAM_TYPE_AUDIO = 2
AVbinStreamType = ctypes.c_int

AVBIN_SAMPLE_FORMAT_U8 = 0
AVBIN_SAMPLE_FORMAT_S16 = 1
AVBIN_SAMPLE_FORMAT_S24 = 2
AVBIN_SAMPLE_FORMAT_S32 = 3
AVBIN_SAMPLE_FORMAT_FLOAT = 4
AVbinSampleFormat = ctypes.c_int

AVBIN_LOG_QUIET = -8
AVBIN_LOG_PANIC = 0
AVBIN_LOG_FATAL = 8
AVBIN_LOG_ERROR = 16
AVBIN_LOG_WARNING = 24
AVBIN_LOG_INFO = 32
AVBIN_LOG_VERBOSE = 40
AVBIN_LOG_DEBUG = 48
AVbinLogLevel = ctypes.c_int

AVbinFileP = ctypes.c_void_p
AVbinStreamP = ctypes.c_void_p

Timestamp = ctypes.c_int64

class AVbinFileInfo(ctypes.Structure):
    _fields_ = [
        ('structure_size', ctypes.c_size_t),
        ('n_streams', ctypes.c_int),
        ('start_time', Timestamp),
        ('duration', Timestamp),
        ('title', ctypes.c_char * 512),
        ('author', ctypes.c_char * 512),
        ('copyright', ctypes.c_char * 512),
        ('comment', ctypes.c_char * 512),
        ('album', ctypes.c_char * 512),
        ('year', ctypes.c_int),
        ('track', ctypes.c_int),
        ('genre', ctypes.c_char * 32),
    ]

class _AVbinStreamInfoVideo8(ctypes.Structure):
    _fields_ = [
        ('width', ctypes.c_uint),
        ('height', ctypes.c_uint),
        ('sample_aspect_num', ctypes.c_uint),
        ('sample_aspect_den', ctypes.c_uint),
        ('frame_rate_num', ctypes.c_uint),
        ('frame_rate_den', ctypes.c_uint),
    ]

class _AVbinStreamInfoAudio8(ctypes.Structure):
    _fields_ = [
        ('sample_format', ctypes.c_int),
        ('sample_rate', ctypes.c_uint),
        ('sample_bits', ctypes.c_uint),
        ('channels', ctypes.c_uint),
    ]

class _AVbinStreamInfoUnion8(ctypes.Union):
    _fields_ = [
        ('video', _AVbinStreamInfoVideo8),
        ('audio', _AVbinStreamInfoAudio8),
    ]

class AVbinStreamInfo8(ctypes.Structure):
    _fields_ = [
        ('structure_size', ctypes.c_size_t),
        ('type', ctypes.c_int),
        ('u', _AVbinStreamInfoUnion8)
    ]

class AVbinPacket(ctypes.Structure):
    _fields_ = [
        ('structure_size', ctypes.c_size_t),
        ('timestamp', Timestamp),
        ('stream_index', ctypes.c_int),
        ('data', ctypes.POINTER(ctypes.c_uint8)),
        ('size', ctypes.c_size_t),
    ]

AVbinLogCallback = ctypes.CFUNCTYPE(None,
    ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p)

av.avbin_get_version.restype = ctypes.c_int
av.avbin_get_ffmpeg_revision.restype = ctypes.c_int
av.avbin_get_audio_buffer_size.restype = ctypes.c_size_t
av.avbin_have_feature.restype = ctypes.c_int
av.avbin_have_feature.argtypes = [ctypes.c_char_p]

av.avbin_init.restype = AVbinResult
av.avbin_set_log_level.restype = AVbinResult
av.avbin_set_log_level.argtypes = [AVbinLogLevel]
av.avbin_set_log_callback.argtypes = [AVbinLogCallback]

av.avbin_open_filename.restype = AVbinFileP
av.avbin_open_filename.argtypes = [ctypes.c_char_p]
av.avbin_close_file.argtypes = [AVbinFileP]
av.avbin_seek_file.argtypes = [AVbinFileP, Timestamp]
av.avbin_file_info.argtypes = [AVbinFileP, ctypes.POINTER(AVbinFileInfo)]
av.avbin_stream_info.argtypes = [AVbinFileP, ctypes.c_int,
                                 ctypes.POINTER(AVbinStreamInfo8)]

av.avbin_open_stream.restype = ctypes.c_void_p
av.avbin_open_stream.argtypes = [AVbinFileP, ctypes.c_int]
av.avbin_close_stream.argtypes = [AVbinStreamP]

av.avbin_read.argtypes = [AVbinFileP, ctypes.POINTER(AVbinPacket)]
av.avbin_read.restype = AVbinResult
av.avbin_decode_audio.restype = ctypes.c_int
av.avbin_decode_audio.argtypes = [AVbinStreamP,
    ctypes.c_void_p, ctypes.c_size_t,
    ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
av.avbin_decode_video.restype = ctypes.c_int
av.avbin_decode_video.argtypes = [AVbinStreamP,
    ctypes.c_void_p, ctypes.c_size_t,
    ctypes.c_void_p]


def get_version():
    return av.avbin_get_version()


def timestamp_from_avbin(timestamp):
    return float(timestamp) / 1000000


def timestamp_to_avbin(timestamp):
    return int(timestamp * 1000000)

if __name__ == "__main__":
    av.avbin_init_options(None)

    meeja_file = av.avbin_open_filename(asbytes_filename('../video/default_sound.mpg'))
    #meeja_file = av.avbin_open_filename(asbytes_filename('../music/transylvania.ogg'))
    if not file:
        print("not file :'(")
        raise Exception("not file :'( :'(")

    file_info = AVbinFileInfo()
    file_info.structure_size = ctypes.sizeof(file_info)
    print(av.avbin_file_info(meeja_file, ctypes.byref(file_info)))

    print('!!! AVbinFile(Info?)')
    for (s, _) in file_info._fields_:
        print(s, getattr(file_info, s))

    # note to self: duration is complete shit
    # (comparison: vlc never goes past 00:00 even though it takes about 5 secs. duration says 0.04s)
    #_duration = timestamp_from_avbin(file_info.duration)

    n_streams = file_info.n_streams
    stream_type_clunk = {AVBIN_STREAM_TYPE_VIDEO: 'video',
                         AVBIN_STREAM_TYPE_AUDIO: 'audio',
                         AVBIN_STREAM_TYPE_UNKNOWN: 'unknown'}

    for i in range(0, n_streams):
        print('STREAM #' + str(i))
        stream_info = AVbinStreamInfo8()
        stream_info.structure_size = ctypes.sizeof(stream_info)
        print(av.avbin_stream_info(meeja_file, i, ctypes.byref(stream_info)))


        stream_type = stream_type_clunk[stream_info.type]
        print('type ' + str(stream_type))

    packet = AVbinPacket()
    packet.structure_size = ctypes.sizeof(packet)

    while av.avbin_read(meeja_file, packet) == AVBIN_RESULT_OK:
        for (s, _) in packet._fields_:
            print(s, getattr(packet, s))
        print('!')

        #for (s, _) in stream_info.u.



