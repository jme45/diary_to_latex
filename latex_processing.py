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
from typing import Optional


class FileNotFound(Exception):
    pass


class TxtFile:
    """
    Class for opening txt files and manipulating the content, so they can be
    processed by latex. to_latex() is the principal callable method.
    """

    # String needed as a temporary replacement. Choose something that is
    # unlikely to appear in the text itself.
    placeholder_str = "XPlaCeHolDerX"
    n_dollar_sep = 20

    def __init__(self, filename):
        self.filename = Path(filename)

    def _detect_encoding(self, content: str) -> str:
        """Return encoding of a file opened in binary mode."""
        detector = chardet.universaldetector.UniversalDetector()
        detector.feed(content)
        detector.close()
        result = detector.result
        return result["encoding"]

    def _process_special_characters(self, content: str) -> str:
        """
        The documents contain several characters Latex cannot handle.
        Replace with Latex friendly versions.
        """
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

        # Search for two dollar signs separated by fewer than n_dollar_sep characters,
        # and replace them by the placeholder_str.

        # Need to assemble regex search string, since f strings don't work here.
        regex_search = r"\$([^$]{1," + str(self.n_dollar_sep) + "}?)\$"
        regex_substitution = self.placeholder_str + r"\1" + self.placeholder_str
        content = re.sub(regex_search, regex_substitution, content)

        # Now replace remaining $ with \$, as these will be genuine dollar signs.
        content = content.replace("$", "\\$")
        # And replace the placeholder with single $ again, to re-enable math mode.
        content = content.replace(self.placeholder_str, "$")

        # replace å with \aa and same for capitals (for Swedish).
        content = content.replace("å", "\\aa ")
        content = content.replace("Å", "\\AA ")

        # replace ñ with \~n
        content = content.replace("ñ", "\\~n")

        # Put in the new lines which latex ignores.
        # Want to replace multiple new lines with a placeholder
        # first (something that won't occur).
        # Then replace remaining new lines with \\,
        # then replace placeholder with two new lines (all that latex cares about).
        content = re.sub("[\n]{2,}", self.placeholder_str, content)
        content = content.replace("\n", "\\\\\n")
        content = content.replace(self.placeholder_str, "\n\n")

        return content

    def to_latex(self) -> str:
        """
        Turn the TextFile object into a latex compatible string.
        :return: Latex compatible string.
        """
        # Check if the file exists.
        if not self.filename.exists():
            raise FileNotFound(f"File '{self.filename}' not found.")

        try:
            with open(self.filename, "rb") as file:
                # Read the content of the file
                content = file.read()
        except FileNotFoundError:
            raise FileNotFound(f"File '{self.filename}' not found.")

        # Detect the encoding
        encoding = self._detect_encoding(content)

        # Decoding should work, since we detected the encoding style, but it could
        # fail, since detecting the encoding is probabilistic.
        try:
            # Decode the content using the detected encoding
            decoded_content = content.decode(encoding)
        except UnicodeDecodeError as e:
            raise ValueError(f"Error decoding file '{self.filename}': {e}")

        decoded_content = self._process_special_characters(decoded_content)

        # Split the content into lines
        lines = decoded_content.split("\n")

        # Wrap the first line with LaTeX \section{...}, since that is the
        # title of the section.
        if lines:
            lines[0] = "\\section{" + lines[0] + "}"

        # Join the modified lines back into a string, separated by new lines.
        modified_content = "\n".join(lines)

        return modified_content


class TexDocument:
    """
    Class for generating a Latex document.
    """

    def __init__(
        self,
        txt_file_names: list[str],
        preamble_file_name: str,
        output_file_name: Optional[str],
    ):
        self.txt_file_names = txt_file_names
        self.preamble_file_name = Path(preamble_file_name)
        if output_file_name is not None:
            self.output_file_name = Path(output_file_name)
        else:
            self.output_file_name = None

        # initialise an empty list with chapter names
        self.chapters = []
        # initialise last chapter name as None
        self.last_chapter_name = None

    def generate(self) -> str:
        """Generate the Latex code for the entire document."""

        # Initialize the LaTeX document string with the preamble
        latex_content = self._read_file_content(self.preamble_file_name)

        # Add the "\begin{document}" string.
        latex_content += "\n\\begin{document}\n"  ###.encode()

        # Add the "\maketitle" string.
        latex_content += "\n\\maketitle\n\n"  ###.encode()

        # Add table of contents.
        latex_content += "\n\\tableofcontents\n\n\n"  ###.encode()

        # Iterate through each txt file, generate TxtFile object, and add to the LaTeX content
        for txt_file_name in self.txt_file_names:
            # Add a new chapter, if needed.
            latex_content += self._chapter_string(txt_file_name)
            txt_file = TxtFile(txt_file_name)
            try:
                latex_content += txt_file.to_latex() + "\n" * 3
            except FileNotFound as e:
                return f"Error: {e}"

        # Add the "\end{document}" string
        latex_content += "\n\\end{document}"

        return latex_content

    def save(self) -> None:
        """Save Latex code to output file"""
        # Generate the LaTeX content
        latex_content = self.generate()

        # Save the LaTeX content to the output file
        with open(self.output_file_name, "w") as output_file:
            output_file.write(latex_content)

    @staticmethod
    def _read_file_content(filename: Path) -> str:
        """Read content of file, e.g. for preamble.tex"""
        try:
            with open(filename, "r") as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFound(f"File '{filename}' not found.")

    @staticmethod
    def _chapter_name_from_txt_file(txt_file: Path) -> str:
        """
        Chapter name is determined by parent directory.

        It removes the diary_ part of the directory, replaces
        underscore with space and capitalises the first letters.
        :param txt_file:
        :return: Chapter name, derived from directory name.
        """
        # Split the parent directory name into components.
        parent = txt_file.parent.stem
        cmpts = parent.split("_")
        assert cmpts[0] == "diary", "each directory must be called 'diary_...' "

        # Reassemble components, ignoring the first part (diary) and capitalise
        # first letter.
        chapter_name = " ".join(c.title() for c in cmpts[1:])

        return chapter_name

    def _chapter_string(self, txt_file_name: Path) -> str:
        """
        Return "\chapter{<new_chapter_name>}" if a new chapter name is needed.

        Get the name for the new chapter. If it's the same as for the previous
        chapter, return "" and do nothing. If it's different, add the name
        of the new chapter to the list of chapters, update
        self.last_chapter_name and return a latex string to start a new chapter.

        :param txt_file_name: name of the text file
        :return: "\chapter{NEW_CHAPTER_NAME}\n" or ""
        """

        chapter_name = self._chapter_name_from_txt_file(txt_file_name)
        if chapter_name == self.last_chapter_name:
            return ""
        else:
            self.chapters.append(chapter_name)
            self.last_chapter_name = chapter_name
            return f"\chapter{{{chapter_name}}}\n\n"
