import pytest
from pathlib import Path
from latex_processing import TxtFile, TexDocument, FileNotFound


@pytest.fixture
def example_text_file(tmp_path):
    tmp_path = tmp_path / "diary_test"
    tmp_path.mkdir(parents=True, exist_ok=True)
    file_path = tmp_path / "example.txt"
    with open(file_path, "w") as file:
        file.write("This is some text with $math$.\n\nHello.")
    return file_path


def test_textfile_to_latex(example_text_file):
    text_file = TxtFile(example_text_file)
    result = text_file.to_latex()
    expected = "\\section{This is some text with $math$.}\n\nHello."
    assert result == expected


def test_textfile_to_latex_file_not_found():
    with pytest.raises(FileNotFound, match=r"File 'non_existent_file.txt' not found."):
        text_file = TxtFile("non_existent_file.txt")
        text_file.to_latex()


def test_texdocument_generate_save(tmp_path, example_text_file):
    preamble_content = "\\documentclass{article}\n\\title{My Title}\n"
    preamble_file = tmp_path / "preamble.tex"
    with open(preamble_file, "w") as preamble:
        preamble.write(preamble_content)

    output_file = tmp_path / "output.tex"

    tex_document = TexDocument(
        [example_text_file], str(preamble_file), str(output_file)
    )
    tex_document.save()

    assert output_file.exists()

    with open(output_file, "r") as result_file:
        result_content = result_file.read()
        expected_content = (
            preamble_content
            + "\n"
            + "\\begin{document}\n\n"
            + "\\maketitle\n\n\n"
            + "\\tableofcontents\n\n\n"
            + "\\chapter{Test}\n\n"
            + "\\section{This is some text with $math$.}\n\n"
            + "Hello.\n\n\n\n"
            + "\\end{document}"
        )

        assert result_content == expected_content, result_content


def test_texdocument_chapter_name_from_txt_file():
    tex_document = TexDocument([], "", "")
    txt_file = Path("diary_example") / "2000_01_01.txt"
    chapter_name = tex_document._chapter_name_from_txt_file(txt_file)
    assert chapter_name == "Example"

    txt_file = Path("diary_long_example") / "2000_01_01.txt"
    chapter_name = tex_document._chapter_name_from_txt_file(txt_file)
    assert chapter_name == "Long Example"
