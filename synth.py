import sys
import os
import argparse
import simpleaudio
import nltk
import string
import numpy

# Sample rate constant
RATE = 16000


class Utterance:

    def __init__(self, utterance):
        """
        Initialize utterance.
        - `filter` (set): punctuation to be removed from the utterance.
        - `lexicon` (dict): pronunciation lexicon (CMUdict).
        - `utterance` (str): input text.
        - `phones` (list): utterance phonemes.
        """

        # Initialize token filter and pronunciation lexicon
        self.filter = set(string.punctuation)
        self.lexicon = nltk.corpus.cmudict.dict()
        self.utterance = utterance

        # Tokenize and extract phones from input utterance
        self.phones = []
        for word in self.get_words(utterance):
            for phone in self.get_phones(word):
                self.phones.append(phone)

    def get_words(self, utterance):
        """
        Return tokenized utterance without punctuation.
        """
        words = []
        for word in nltk.word_tokenize(utterance):

            # Exclude words in filter
            if word in self.filter:
                continue

            # Exit if word contains non-alphabetic characters
            if not word.isalpha():
                sys.exit("Text must only contain alphabetic characters")
            words.append(word.lower())

        return words

    def get_phones(self, word, variant=0):
        """
        Given a word, return a normalized phonemic transcription
        if available in pronunciation lexicon. Otherwise, exit
        program.
        """
        if word not in self.lexicon:
            sys.exit(f"Couldn't transcribe '{word}'")

        # Select variant pronunciation if it exists
        lex_entry = self.lexicon[word]
        if variant <= len(lex_entry) - 1:
            pronunciation = lex_entry[variant]
        else:
            pronunciation = lex_entry[0]

        return map(lambda phone: phone.lower().rstrip("012"), pronunciation)

    def get_diphones(self):
        """
        Expand phone sequence into a diphone sequence.
        """

        # Initialize diphone sequence
        diphones = [[None, self.phones[0]]]

        # Expand phones into diphones
        for i in range(len(self.phones) - 1):
            ph1 = self.phones[i]
            ph2 = self.phones[i + 1]
            diphones.append([ph1, ph2])

        # Add last diphone to sequence
        diphones.append([self.phones[len(self.phones) - 1], None])
        return diphones


class Synth:

    def __init__(self, diphones, directory):
        """
        Initialize synthesizer.
        - `diphones` (list): sequence of diphones
        - `audio` (dict): dictionary of filename-audio pairs
        """
        self.diphones = diphones

        # Create mapping from diphone filenames to audio
        self.audio = {}
        for diphone in self.diphones:
            filename = self.get_filename(diphone)
            if filename not in self.audio:

                # Ensure that file exists
                path = os.path.join(directory, filename)
                if not os.path.isfile(path):
                    sys.exit(f"Couldn't locate '{filename}'")

                # Load its contents and add to dictionary
                audio = simpleaudio.Audio()
                audio.load(path)
                self.audio[filename] = audio

    def get_filename(self, diphone):
        """
        Given a diphone, return its corresponding filename.
        """
        ph1 = diphone[0] if diphone[0] is not None else "pau"
        ph2 = diphone[1] if diphone[1] is not None else "pau"
        return f"{ph1}-{ph2}.wav"

    def get_audio(self, rate=RATE):
        """
        Return synthesized output as an `Audio` object containing
        the concatenated audio for the input diphone sequence.
        """

        # Create audio sequence from diphones
        output_audio = []
        for diphone in self.diphones:
            filename = self.get_filename(diphone)
            audio = self.audio[filename]
            output_audio.append(audio.data)

        # Instantiate output `Audio` object
        output = simpleaudio.Audio(rate=rate)

        # Concatenate audio and rescale
        output.data = numpy.concatenate(output_audio)
        output.rescale(1.0)
        return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Basic text-to-speech synthesis based on diphone unit selection."
        )
    parser.add_argument("--diphones", default="./diphones", help="Directory containing the diphone files.")
    parser.add_argument("--play", action="store_true", default=True, help="Play the output audio.")
    parser.add_argument("--save", default=None, help="Save the output audio.")
    parser.add_argument("--text", required=True, help="Text to be synthesised.")
    args = parser.parse_args()

    # Extract diphones from input text
    utterance = Utterance(args.text)
    diphones = utterance.get_diphones()

    # Synthesize diphone sequence
    synth = Synth(diphones, args.diphones)
    output = synth.get_audio()

    # Play and save output synthesis
    if args.play:
        output.play()
    if args.save:
        output.save(args.save)
