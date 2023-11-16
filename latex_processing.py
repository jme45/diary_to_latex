"""
The classes needed to convert my diary entries into a latex document.

My diary entries are plain txt files with the following structure.
* First line: Date. This is to be converted to the section heading
* blank line
* the rest of the entry. This can just be added verbatim to the latex document

This was generated with the help of ChatGPT, which made coding faster.
"""

from pathlib import Path
import chardet
import re


class FileNotFound(Exception):
    pass


class TextFile:
    placeholder_str = "XPlaCeHolDerX"
    n_dollar_sep = 20

    def __init__(self, filename):
        self.filename = Path(filename)

    def _detect_encoding(self, content):
        detector = chardet.universaldetector.UniversalDetector()
        detector.feed(content)
        detector.close()
        result = detector.result
        return result["encoding"]

    def _process_special_characters(self, content):
        # Replace \n\r with \n, that is, remove the carriage return.
        # Some editors I used, used \n\r, some just \n and \n\r is not needed.
        content = content.replace("\r\n", "\n")

        # Replace & with \&, so latex doesn't crash.
        content = content.replace("&", "\\&")

        # Replace funny Apple quotes with normal quotes.
        content = content.replace("“", '"')

        # dollar signs will in general also be dollar signs, not maths.
        # Use as proxy for it being maths that the two dollar signs are separated
        # by fewer than 20 characters, I didn't usually write long equations.
        # So first replace $ with placeholder, if they are separated by
        # fewer than n_dollar_sep characters
        # Need to assemble regex search string, since f strings don't work here.
        regex_search = r"\$([^$]{1," + str(self.n_dollar_sep) + "}?)\$"
        regex_substitution = self.placeholder_str + r"\1" + self.placeholder_str
        content = re.sub(regex_search, regex_substitution, content)
        # Now replace remaining $ with \$
        content = content.replace("$", "\\$")
        # And replace the placeholder with single $ again
        content = content.replace(self.placeholder_str, "$")

        # replace å with \aa and same for capitals (for Swedish).
        content = content.replace("å", "\\aa ")

        # replace Viñales with \~n
        content = content.replace("ñ", "\\~n")

        # Put in the new lines which latex ignores.
        # Want to replace multiple new lines with a placeholder
        # first (something that won't occur).
        # Then replace remaining new lines, then replace
        # placeholder with two new lines (all that latex cares about).
        content = re.sub("[\n]{2,}", self.placeholder_str, content)
        content = content.replace("\n", "\\\\\n")
        content = content.replace(self.placeholder_str, "\n\n")

        return content

    def to_latex(self):
        # Check if the file exists
        if not self.filename.exists():
            raise FileNotFound(f"File '{self.filename}' not found.")

        try:
            with open(self.filename, "rb") as file:
                # Read the content of the file
                content = file.read()

            # Detect the encoding
            encoding = self._detect_encoding(content)

            # Decode the content using the detected encoding
            decoded_content = content.decode(encoding)

            decoded_content = self._process_special_characters(decoded_content)

            decoded_content = decoded_content  ###.encode()

            # Split the content into lines
            lines = decoded_content.split("\n")
        except FileNotFoundError:
            raise FileNotFound(f"File '{self.filename}' not found.")
        except UnicodeDecodeError as e:
            raise ValueError(f"Error decoding file '{self.filename}': {e}")

        # Wrap the first line with LaTeX \section{...}
        if lines:
            lines[0] = "\\section{" + lines[0] + "}"

        # Join the modified lines back into a string
        modified_content = "\n".join(lines)

        return modified_content


class TexDocument:
    def __init__(self, txt_files, preamble_file_name, output_file_name):
        self.txt_files = txt_files
        self.preamble_file_name = Path(preamble_file_name)
        if output_file_name is not None:
            self.output_file_name = Path(output_file_name)
        else:
            self.output_file_name = None

    def generate(self):
        # Initialize the LaTeX document string with the preamble
        latex_content = self._read_file_content(self.preamble_file_name)

        # Add the "\begin{document}" string
        latex_content += "\n\\begin{document}\n"  ###.encode()

        # Add the "\maketitle" string
        latex_content += "\n\\maketitle\n\n"  ###.encode()

        # Add table of contents
        latex_content += "\n\\tableofcontents\n\n\n"  ###.encode()

        # Iterate through each txt file, generate TextFile object, and add to the LaTeX content
        for txt_file in self.txt_files:
            text_file = TextFile(txt_file)
            try:
                latex_content += text_file.to_latex() + "\n"  ###.encode()
            except FileNotFound as e:
                return f"Error: {e}"

        # Add the "\end{document}" string
        latex_content += "\n\\end{document}"

        return latex_content

    def save(self):
        # Generate the LaTeX content
        latex_content = self.generate()

        # Save the LaTeX content to the output file
        with open(self.output_file_name, "w") as output_file:
            output_file.write(latex_content)

    @staticmethod
    def _read_file_content(filename):
        try:
            with open(filename, "r") as file:
                return file.read()  ###.encode('utf-8')
        except FileNotFoundError:
            raise FileNotFound(f"File '{filename}' not found.")


if __name__ == "__main__":
    filename = Path(
        "/Users/jonathan/Documents/Jonathan/mail/diary_cambridge/2008_05_04.txt"
    )
    tf = TextFile(filename)
    print(tf.to_latex())
