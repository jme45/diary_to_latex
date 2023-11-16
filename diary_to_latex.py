"""
Main function for running diary to latex conversion.
"""

import argparse
import pathlib
from pathlib import Path
import glob
from latex_processing import TexDocument, FileNotFound


def main():
    parser = argparse.ArgumentParser(
        prog="diary_to_latex",
        description="Generate and save LaTeX document from diary txt files.",
    )
    parser.add_argument(
        "--txt_input_files",
        type=pathlib.Path,
        nargs="*",
        help="List of input txt files. Wildcards like *.txt are supported.",
    )
    parser.add_argument(
        "--preamble_file",
        type=str,
        default="preamble.tex",
        help="Preamble file name (default: preamble.tex).",
    )
    parser.add_argument(
        "--output_file_name",
        type=str,
        help="Output file name for the generated LaTeX document.",
    )

    args = parser.parse_args()

    # Convert the list of files to a list of paths, possibly redundant
    txt_files_list = [Path(file) for file in args.txt_input_files]
    # sort by date, can just sort sting, if take filename
    txt_files_list = sorted(txt_files_list, key=lambda x: x.stem)

    # Create a TexDocument object and generate/save the LaTeX content
    tex_document = TexDocument(
        txt_files_list, args.preamble_file, args.output_file_name
    )

    # If no output path is given, just print latex output to screen,
    # otherwise write to file.
    if tex_document.output_file_name is None:
        print(f"Printing latex output to screen: \n{tex_document.generate()}")
    else:
        try:
            tex_document.save()
            print(
                f"LaTeX document successfully generated and saved to '{args.output_file_name}'."
            )
        except FileNotFound as e:
            print(f"Error: {e}. Unable to write latex document.")


if __name__ == "__main__":
    main()
