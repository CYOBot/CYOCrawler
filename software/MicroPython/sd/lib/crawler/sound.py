import os
import struct
import math
import time
from machine import Pin, I2S, ADC

class Microphone:
    def __init__(self):
        self.pin = ADC(Pin(32))
    
    def read(self, buffer=1):
        data = []
        for i in range(buffer):
            data.append(self.pin.read())
        return data


# The MIT License (MIT)
# Copyright (c) 2022 Mike Teachman
# https://opensource.org/licenses/MIT
#
# MicroPython Class used to control playing a WAV file using an I2S amplifier or DAC module
# - control playback with 5 methods:
#     - play()
#     - pause()
#     - resume()
#     - stop()
#     - isplaying()
# Example:
#    wp = WavPlayer(id=I2S_ID,
#                   sck_pin=Pin(SCK_PIN),
#                   ws_pin=Pin(WS_PIN),
#                   sd_pin=Pin(SD_PIN),
#                   ibuf=BUFFER_LENGTH_IN_BYTES)
#    wp.play("YOUR_WAV_FILE.wav", loop=True)
#
# All methods are non-blocking.
# The WAV file header is parsed in the play() method to get audio parameters

class WavPlayer:
    PLAY = 0
    PAUSE = 1
    RESUME = 2
    FLUSH = 3
    STOP = 4

    def __init__(self, id, sck_pin, ws_pin, sd_pin, ibuf, root="/sd"):
        self.id = id
        self.sck_pin = sck_pin
        self.ws_pin = ws_pin
        self.sd_pin = sd_pin
        self.ibuf = ibuf
        self.root = root.rstrip("/") + "/"
        self.state = WavPlayer.STOP
        self.wav = None
        self.loop = False
        self.format = None
        self.sample_rate = None
        self.bits_per_sample = None
        self.first_sample_offset = None
        self.num_read = 0
        self.sbuf = 1000
        self.nflush = 0

        # allocate a small array of blank audio samples used for silence
        self.silence_samples = bytearray(self.sbuf)

        # allocate audio sample array buffer
        self.wav_samples_mv = memoryview(bytearray(3200))

    def i2s_callback(self, arg):
        if self.state == WavPlayer.PLAY:
            self.num_read = self.wav.readinto(self.wav_samples_mv)
            # end of WAV file?
            if self.num_read == 0:
                # end-of-file
                if self.loop == False:
                    self.state = WavPlayer.FLUSH
                else:
                    # advance to first byte of Data section
                    _ = self.wav.seek(self.first_sample_offset)
                _ = self.audio_out.write(self.silence_samples)
            else:
                _ = self.audio_out.write(self.wav_samples_mv[: self.num_read])
        elif self.state == WavPlayer.RESUME:
            self.state = WavPlayer.PLAY
            _ = self.audio_out.write(self.silence_samples)
        elif self.state == WavPlayer.PAUSE:
            _ = self.audio_out.write(self.silence_samples)
        elif self.state == WavPlayer.FLUSH:
            # Flush is used to allow the residual audio samples in the
            # internal buffer to be written to the I2S peripheral.  This step
            # avoids part of the sound file from being cut off
            if self.nflush > 0:
                self.nflush -= 1
                _ = self.audio_out.write(self.silence_samples)
            else:
                self.wav.close()
                self.audio_out.deinit()
                self.state = WavPlayer.STOP
        elif self.state == WavPlayer.STOP:
            pass
        else:
            raise SystemError("Internal error:  unexpected state")
            self.state == WavPlayer.STOP

    def parse(self, wav_file):
        chunk_ID = wav_file.read(4)
        if chunk_ID != b"RIFF":
            raise ValueError("WAV chunk ID invalid")
        chunk_size = wav_file.read(4)
        format = wav_file.read(4)
        if format != b"WAVE":
            raise ValueError("WAV format invalid")
        sub_chunk1_ID = wav_file.read(4)
        if sub_chunk1_ID != b"fmt ":
            raise ValueError("WAV sub chunk 1 ID invalid")
        sub_chunk1_size = wav_file.read(4)
        audio_format = struct.unpack("<H", wav_file.read(2))[0]
        num_channels = struct.unpack("<H", wav_file.read(2))[0]

        if num_channels == 1:
            self.format = I2S.MONO
        else:
            self.format = I2S.STEREO

        self.sample_rate = struct.unpack("<I", wav_file.read(4))[0]
        byte_rate = struct.unpack("<I", wav_file.read(4))[0]
        block_align = struct.unpack("<H", wav_file.read(2))[0]
        self.bits_per_sample = struct.unpack("<H", wav_file.read(2))[0]

        # usually the sub chunk2 ID ("data") comes next, but
        # some online MP3->WAV converters add
        # binary data before "data".  So, read a fairly large
        # block of bytes and search for "data".

        binary_block = wav_file.read(200)
        offset = binary_block.find(b"data")
        if offset == -1:
            raise ValueError("WAV sub chunk 2 ID not found")

        self.first_sample_offset = 44 + offset

    def play(self, wav_file, loop=False):
        if os.listdir(self.root).count(wav_file) == 0:
            raise ValueError("%s: not found" % wav_file)
        if self.state == WavPlayer.PLAY:
            raise ValueError("already playing a WAV file")
        elif self.state == WavPlayer.PAUSE:
            raise ValueError("paused while playing a WAV file")
        else:
            self.wav = open(self.root + wav_file, "rb")
            self.loop = loop
            self.parse(self.wav)

            self.audio_out = I2S(
                self.id,
                sck=self.sck_pin,
                ws=self.ws_pin,
                sd=self.sd_pin,
                mode=I2S.TX,
                bits=self.bits_per_sample,
                format=self.format,
                rate=self.sample_rate,
                ibuf=self.ibuf,
            )

            # advance to first byte of Data section in WAV file
            _ = self.wav.seek(self.first_sample_offset)
            self.audio_out.irq(self.i2s_callback)
            self.nflush = self.ibuf // self.sbuf + 1
            self.state = WavPlayer.PLAY
            _ = self.audio_out.write(self.silence_samples)

    def resume(self):
        if self.state != WavPlayer.PAUSE:
            raise ValueError("can only resume when WAV file is paused")
        else:
            self.state = WavPlayer.RESUME

    def pause(self):
        if self.state == WavPlayer.PAUSE:
            pass
        elif self.state != WavPlayer.PLAY:
            raise ValueError("can only pause when WAV file is playing")

        self.state = WavPlayer.PAUSE

    def stop(self):
        self.state = WavPlayer.FLUSH

    def isplaying(self):
        if self.state != WavPlayer.STOP:
            return True
        else:
            return False
        
class Speaker:
    def __init__(self):
        self.SCK_PIN = 25
        self.WS_PIN = 26
        self.SD_PIN = 14
        self.I2S_ID = 0
        self.BUFFER_LENGTH_IN_BYTES = 3200
        self.wp = WavPlayer(
            id=self.I2S_ID,
            sck_pin=Pin(self.SCK_PIN),
            ws_pin=Pin(self.WS_PIN),
            sd_pin=Pin(self.SD_PIN),
            ibuf=self.BUFFER_LENGTH_IN_BYTES,
        )
    
    def make_tone(self, rate, bits, frequency, volume=5):
        # create a buffer containing the pure tone samples
        samples_per_cycle = rate // frequency
        sample_size_in_bytes = bits // 8
        samples = bytearray(samples_per_cycle * sample_size_in_bytes)
        # volume_reduction_factor = 32
        # range = pow(2, bits) // 2 // volume_reduction_factor
        max_range = (pow(2, bits) // 2)
        range =  int((max_range / 5) * volume)

        if bits == 16:
            format = "<h"
        else:  # assume 32 bits
            format = "<l"

        for i in range(samples_per_cycle):
            sample = range + int((range - 1) * math.sin(2 * math.pi * i / samples_per_cycle))
            struct.pack_into(format, samples, i * sample_size_in_bytes, sample)

        return samples
    
    def play_tone(self, frequency=440, volume=5, duration=1):
        # ======= AUDIO CONFIGURATION =======
        SAMPLE_SIZE_IN_BITS = 16
        FORMAT = I2S.MONO  # only MONO supported in this example
        SAMPLE_RATE_IN_HZ = 22_050
        # ======= AUDIO CONFIGURATION =======

        if volume > 5:
            volume = 5
            print("Warning, volume range is [0, 5]")
        
        samples = self.make_tone(SAMPLE_RATE_IN_HZ, SAMPLE_SIZE_IN_BITS, frequency=frequency, volume=volume)
        audio_out = I2S(
            self.I2S_ID,
            sck=self.SCK_PIN,
            ws=self.WS_PIN,
            sd=self.SD_PIN,
            mode=I2S.TX,
            bits=SAMPLE_SIZE_IN_BITS,
            format=FORMAT,
            rate=SAMPLE_RATE_IN_HZ,
            ibuf=self.BUFFER_LENGTH_IN_BYTES,
        )

        try:
            cur_time = time.time()
            while time.time() - cur_time < duration:
                num_written = audio_out.write(samples)

        except (KeyboardInterrupt, Exception) as e:
            print("caught exception {} {}".format(type(e).__name__, e))

        # cleanup
        audio_out.deinit()
    
    def play(self, filename="music-16k-16bits-mono.wav"):
        self.wp.play(filename, loop=False)

        while self.wp.isplaying() == True:
            # do something else here
            pass
