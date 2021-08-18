import pyaudio
import wave


class LinuxInternalSoundRecorder:
    def __init__(self):
        self.base_save_path = '/home/discoverious/Documents/PycharmProjects/youtube_shorts_project/temperary_database/musics'

    def start_recording(self, wave_output_filename, record_seconds):
        '''
        Record internal sound as wave file

        :param wave_output_filename: Just 'file_name'
        :param record_seconds: int()
        :return: output wave file save path
        '''
        chunk = 1024
        format = pyaudio.paInt16
        channels = 2
        rate = 44100
        file_save_path = f"{self.base_save_path}/{wave_output_filename}.wav"

        p = pyaudio.PyAudio()

        stream = p.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)

        print("* recording")

        frames = []

        for i in range(0, int(rate / chunk * record_seconds)):
            data = stream.read(chunk)
            frames.append(data)

        print("* done recording")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(file_save_path, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        return file_save_path
