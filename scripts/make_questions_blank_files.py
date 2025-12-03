"""
    A command-line tool for creating blank question-files.

    Parameters:
    `file`: a string, the path to the file containing the list of questions,
    `subfolder`: a string, the path to the folder where the question files will be created,
    `name`: a string, a new name for the modified file.

    Reads lines sequentially from the file containing the list of questions.
    For each question, it creates a blank markdown file with only a title equal to the question.
    The question itself is updated to a link to the blank markdown file for that question.

"""

import os
import argparse
from pathlib import Path
import re
import secrets
from typing import Optional


def parse_line(line: str) -> Optional[tuple[str, str]]:
    m = re.fullmatch(r'\s*(\d+\.\s+)([^\[].+\S)\s*', line)
    if m is None:
        return None
    else:
        return m.group(1), m.group(2)


def create_blank_files(file_path: Path, subfolder_path: Path, name: str):
    if not (file_path.exists() and file_path.is_file()):
        raise ValueError("There is no such file")

    if os.path.isabs(subfolder_path):
        if not subfolder_path.is_relative_to(file_path.parent):
            raise ValueError("The subfolder must be relative to the file path")
    else:
        subfolder_path = file_path.parent / subfolder_path

    rel_subfolder_path = subfolder_path.relative_to(file_path.parent)

    # Ensure the subfolder exists
    os.makedirs(subfolder_path, exist_ok=True)

    # Read questions from the file
    with open(file_path, 'r') as fp:
        lines = fp.readlines()

    if len(lines) > 1000:
        raise ValueError("Too many lines")

    # Process each question
    processed = 0
    with open(file_path.parent / name, 'w') as fp:
        for line in lines:
            line = line.rstrip()
            line_parts = parse_line(line)
            if line_parts is None:
                fp.write(line)
                fp.write(os.linesep)
            else:
                pref, question = line_parts
                qf_name = f'question_{secrets.token_hex(4)}.md'
                qf_path = rel_subfolder_path / qf_name

                # Update question line
                fp.write(f"{pref}[{question}]({qf_path})")  # Markdown link to file
                fp.write(os.linesep)

                # Create a quesion file
                with open(subfolder_path / qf_name, 'w') as qf:
                    qf.write(f"## {question}")
                    qf.write(os.linesep)

                print(f"Created file {qf_path} for question: {question}")
                processed += 1

    return processed


def main():
    parser = argparse.ArgumentParser(description="Create blank markdown files for questions.")
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Path to the file containing the list of questions."
    )
    parser.add_argument(
        "--subfolder",
        type=str,
        required=True,
        help="Path to the folder where the question files will be created."
    )
    parser.add_argument(
        "--name",
        type=str,
        required=False,
        help="New name for the modified file.",
        default="questions.md"
    )
    args = parser.parse_args()

    processed = create_blank_files(
        file_path=Path(args.file),
        subfolder_path=Path(args.subfolder),
        name=args.name
    )
    print(f"Processed {processed} questions.")


if __name__ == "__main__":
    main()
