## Diphone synthesizer 
Basic [concatenative speech synthesizer](https://en.wikipedia.org/wiki/Concatenative_synthesis) in English. 

### Overview
Basic speech synthesizer to convert input text to a sound waveform containing intelligible speech.
It uses a very simple unit selection and waveform concatenation system, with the acoustic units being individual recordings of [diphones](https://en.wikipedia.org/wiki/Diphone). 

- [`sympleaudio.py`](simpleaudio.py) contains an `Audio` class that acts as an interface with the audio hardware, enabling operations such as saving, loading and playing `.wav` files. 
- [`synth.py`](synth.py) is the main program and contains the following classes:
  - `Utterance`: Performs basic word tokenization and normalization of the input text, converts words to phonemic transcriptions and extracts a sequence of diphones.
  - `Synth`: Takes in a sequence of diphones, reads the contents of their corresponding `.wav` files into `Audio` objects, and concatenates them, allowing to play and/or save the output as another `.wav` file. 
- [directory](directory): path to the directory that contains the `.wav` files for diphone sounds - diphones go from the middle of one speech sound to the middle of the next one, capturing the transition between both sounds.  

### Instructions
#### Required arguments
- `--text`: text to be synthesized.
#### Optional arguments
- `--diphones`: directory containing `.wav` files (`./directory` by default).
- `--play` (default): play synthesized output.
- `--save`: output `.wav` filename. 
#### Example
<p align="center">
<code>python synth.py --text "I sound like a robot" --save robot.wav --play </code> 
</p>
