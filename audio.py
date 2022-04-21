import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from scipy import signal
# from datetime import datetime, timedelta 

# These values can be adapted according to your requirements.
samplerate = 48000
seconds = 3
downsample = 1
input_gain_db = 15
device = 'snd_rpi_i2s_card'

sd.default.device = [device, 0]

def butter_highpass(cutoff, fs, order=5):
    '''
    Helper function for the high-pass filter.
    '''
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=5):
    '''
    High-pass filter for digital audio data.
    '''
    b, a = butter_highpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

def set_gain_db(audiodata, gain_db):
    '''
    This function allows to set the audio gain
    in decibel. Values above 1 or below -1 are set to
    the max/min values.
    '''
    audiodata *= np.power(10, gain_db/10)
    return np.array([1 if s > 1 else -1 if s < -1 else s for s in audiodata], dtype=np.float32)

def process_audio_data(audiodata):
    # Extract mono channels from input data.
    ch1 = np.array(audiodata[::downsample, 0], dtype=np.float32)
    # ch2 = np.array(audiodata[::downsample, 1], dtype=np.float32)

    # High-pass filter the data at a cutoff frequency of 10Hz.
    # This is required because I2S microhones have a certain DC offset
    # which we need to filter in order to amplify the volume later.
    ch1 = butter_highpass_filter(ch1, 10, samplerate)
    # ch2 = butter_highpass_filter(ch2, 10, samplerate)

    # Amplify audio data.
    # Recommended, because the default input volume is very low.
    # Due to the DC offset this is not recommended without using
    # a high-pass filter in advance.
    ch1 = set_gain_db(ch1, input_gain_db)
    # ch2 = set_gain_db(ch2, input_gain_db)

    # Output the data in the same format as it came in.
    # return np.array([[ch1[i], ch2[i]] for i in range(len(ch1))], dtype=np.float32)
    return np.array([[ch1[i]] for i in range(len(ch1))], dtype=np.float32)
    
def record(duration, path):
    # Record audio data for the given duration in seconds.
    rec = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
    # Wait until the recording is done.
    sd.wait()

    # Process the audio data as explained above.
    processed = process_audio_data(rec)

    # Write the processed audio data to a wav file.
    path = path + '/sound.wav'
    write(path, int(samplerate/downsample), processed)
    
    #return path

# time = str(datetime.now())
# path = '/home/pi'
# record(5, path)
