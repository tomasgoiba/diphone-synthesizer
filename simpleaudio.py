import pyaudio
import numpy as np
import wave

# Define format parameter constants
BYTES = 256
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
MAX_AMP = 2**15


class Audio(pyaudio.PyAudio):

    def __init__(self, channels=CHANNELS, rate=RATE, bytes=BYTES, format=FORMAT):
        """
        Initialize interface with audio hardware.
        - `channels` (int): number of audio channels.
        - `rate` (int): rate of audio samples.
        - `bytes`(int): bytes of data to be read from the input stream.
        - `count`(int): count of chunks of data that have been read.
        - `format` (type): type of PyAudio samples
        - `data` (numpy.ndarray): array of audio samples.
        - `nptype` (type): type of elements in `data`.
        - `input_stream` (pyAudio.Stream): input stream.
        - `output_stream`(pyAudio.Stream): output stream.
        """

        # Initialize parent class
        pyaudio.PyAudio.__init__(self)

        # Set format parameters
        self.channels = channels
        self.rate = rate
        self.format = format

        # Initialize data attributes
        self.nptype = self.get_np_type(format)
        self.data = np.array([], dtype=self.nptype)
        self.bytes = bytes
        self.count = 0

        # Initialize input streams
        self.input_stream = None
        self.output_stream = None

    def get_bytes(self):
        """
        Read a `bytes` size chunk of data from the input stream.
        """
        temp_str = self.input_stream.read(self.bytes)
        array = np.fromstring(temp_str, dtype=self.nptype)
        self.data = np.append(self.data, array)

    def put_bytes(self):
        """
        Write a `bytes` size chunk of data to the output stream.
        """

        # Calculate where the current chunk starts and ends
        slice_from = self.count * self.bytes
        slice_to = slice_from + self.bytes - 1

        # Raise error if end of chunk is out of bounds
        if slice_to > len(self.data):
            raise IndexError(f"{slice_to} is out of bounds.")

        # Write current chunk to output stream and update count
        array = self.data[slice_from : slice_to]
        self.output_stream.write(array.tostring())
        self.count += 1

    def open_input_stream(self):
        """
        Make an input stream.
        """

        # Call `open` function from parent class
        self.input_stream = self.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            frames_per_buffer=self.bytes,
            input=True
            )

    def close_input_stream(self):
        """
        Close the input stream.
        """
        self.input_stream.close()
        self.input_stream = None

    def open_output_stream(self):
        """
        Make an output stream.
        """

        # Call `open` function from parent class
        self.output_stream = self.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=True
            )

        # Set count to zero
        self.count = 0

    def close_output_stream(self):
        """
        Close the output stream.
        """
        self.output_stream.close()
        self.output_stream = None

    def play(self):
        """
        Play the current data.
        """

        # Open output stream
        self.open_output_stream()

        # Loop until all data has been written to output stream
        print("Playing...")
        while True:
            try:
                self.put_bytes()
            except IndexError:  # Not enough bytes left
                break
        print("Stopped playing.")

        # Close output stream
        self.close_output_stream()

    def save(self, path):
        """
        Write the data to a WAV file.
        """

        # Convert data to a string
        raw = self.data.tostring()

        # Open output file
        wf = wave.open(path, 'wb')

        # Set header information
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.get_sample_size(self.format))
        wf.setframerate(self.rate)

        # Write data to file
        wf.writeframes(raw)

        # Close output file
        wf.close()

    def load(self, path):
        """
        Load data from a WAV file.
        """

        # Open input file
        wf = wave.open(path, "rb")

        # Get header information
        self.format = self.get_format_from_width(wf.getsampwidth())
        self.nptype = self.get_np_type(self.format)
        self.channels = wf.getnchannels()
        self.rate = wf.getframerate()

        # Initialize data array
        self.data = np.array([], dtype=self.nptype)

        # Read `bytes` size chunk of data from file
        raw = wf.readframes(self.bytes)

        # Loop until data runs out
        while raw:

            # Convert raw string to data and append to `data`
            array = np.fromstring(raw, dtype=self.nptype)
            self.data = np.append(self.data, array)

            # Read next chunk of data
            raw = wf.readframes(self.bytes)

        # Close the file
        wf.close()

    def get_np_type(self, type):
        """
        Map PyAudio sample format `paInt16` to NumPy data type `int16`.
        """
        if type == pyaudio.paInt16:
            return np.int16

    def rescale(self, val):
        """
        Given a scaling factor, rescale the audio data.
        """

        # Ensure value is between 0 and 1
        if not 0 <= val <= 1:
            raise ValueError("Scaling factor should be between 0 and 1.")

        # Find sample with largest absolute value (peak)
        peak = 0
        for i in range(len(self.data) - 1):
            peak = max(peak, abs(self.data[i]))

        # Normalize scaling factor to prevent peak values over `MAX_AMP`
        rescale_factor = val * MAX_AMP / peak

        # Scale all sample values by normalized factor
        self.data = (self.data * rescale_factor).astype(self.nptype)

    def __len__(self):
        """
        Return the number of elements in the data array.
        """
        return self.data.shape[0]
