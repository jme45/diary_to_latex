"""
The classes needed to convert my diary entries into a latex document.

My diary entries are plain txt files with the following structure.
* First line: Date. This is to be converted to the section heading
* blank line
* the rest of the entry. This can just be added verbatim to the latex document

This was generated with the help of ChatGPT, which made coding faster.
"""

from pathlib import Path


class FileNotFound(Exception):
    pass


class TextFile:
    def __init__(self, filename):
        self.filename = Path(filename)

    def to_latex(self):
        # Check if the file exists
        if not self.filename.exists():
            raise FileNotFound(f"File '{self.filename}' not found.")

        with open(self.filename, "r") as file:
            # Read the content of the file
            content = file.read()

        # Split the content into lines
        lines = content.split("\n")

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
        latex_content += "\n\\begin{document}\n"

        # Add the "\maketitle" string
        latex_content += "\n\\maketitle\n\n"

        # Add table of contents
        latex_content += "\n\\tableofcontents\n\n\n"

        # Iterate through each txt file, generate TextFile object, and add to the LaTeX content
        for txt_file in self.txt_files:
            text_file = TextFile(txt_file)
            try:
                latex_content += text_file.to_latex() + "\n"
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
                return file.read()
        except FileNotFoundError:
            raise FileNotFound(f"File '{filename}' not found.")
