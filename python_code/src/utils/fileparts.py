import os


def fileparts(file):
    """
    Splits the file path into directory, filename, extension and subject folder.

    Parameters:
    file_path -- str. The full file path.

    Returns:
    tuple -- (directory, filename, extension)
    """

    directory = os.path.dirname(file)
    basename = os.path.basename(file)
    filename, extension = os.path.splitext(basename)

    subj = directory.split('/')[-1]

    return directory, filename, extension, subj
