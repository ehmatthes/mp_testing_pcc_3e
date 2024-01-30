"""Test all Matplotlib programs.

Chapter 15: Basic plots, random walks
Chapter 16: Weather plots

Overall approach:
- Copy code to a tmp dir.
- Modify code to call savefig() instead of plt.show().
- Compare output files against reference files.

"""

from pathlib import Path
import shutil, os, filecmp

import utils


def test_mpl_squares(tmp_path, python_cmd):
    # Copy program file to temp dir.
    test_file = "chapter_15/plotting_simple_line_graph/mpl_squares.py"
    src_path = Path(__file__).parents[1] / test_file

    dest_path = tmp_path / src_path.name
    shutil.copy(src_path, dest_path)

    # Replace plt.show() with savefig().
    contents = dest_path.read_text()
    save_cmd = 'plt.savefig("output_file.png")'
    contents = contents.replace("plt.show()", save_cmd)

    # Uncomment this to verify that comparison
    #   fails for incorrect image:
    # contents = contents.replace("16", "32")
    
    dest_path.write_text(contents)

    # Run program from tmp path dir.
    os.chdir(tmp_path)
    cmd = f"{python_cmd} {dest_path.name}"
    output = utils.run_command(cmd)

    # Verify file was created, and that it matches reference file.
    output_path = tmp_path / "output_file.png"
    assert output_path.exists()

    # Print output file path, so it's easy to find images.
    print("\n***** mpl_squares output:", output_path)

    reference_filename = src_path.name.replace(".py", ".png")
    reference_file_path = (Path(__file__).parent
            / "reference_files" / reference_filename)
    assert filecmp.cmp(output_path, reference_file_path)

    # Verify text output.
    assert output == ""