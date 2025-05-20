def scheduler(python_code):
    """
    Saves the provided Python code string to a uniquely‑named `.py` file
    inside a `generated_scripts` directory (created if it does not exist).

    Args:
        python_code (str): Python source code to be written.

    Returns:
        str: Absolute path to the newly created Python file.
    """
    import os
    import uuid

    # Ensure the target directory exists (relative to this file)
    output_dir = os.path.join(os.path.dirname(__file__), "generated_scripts")
    os.makedirs(output_dir, exist_ok=True)

    # Generate a unique filename for the new script
    filename = f"script_{uuid.uuid4().hex}.py"
    file_path = os.path.join(output_dir, filename)

    # Write the code to the file
    with open(file_path, "w", encoding="utf-8") as fp:
        fp.write(python_code)

    return file_path