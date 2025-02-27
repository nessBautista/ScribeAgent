# UV by astral
UV is a modern, high-performance Python package manager designed to streamline and accelerate Python development workflows. Developed by Astral (creators of the Ruff linter) and written in Rust, UV combines the functionality of multiple traditional tools like pip, virtualenv, poetry, pyenv, and pip-tools into a unified interface

Installation:

[uv](https://docs.astral.sh/uv/#installation)

# Using UV for dependency management

When you run `uv run hello_world.py`, UV does the following:

UV scans the beginning of the Python file looking for a specific pattern:
```python
# /// script
# dependencies = [
...
# ///
```

2. This is a special marker that UV recognizes as a "script manifest". Think of it like a miniature `requirements.txt` or `pyproject.toml` embedded directly in the script.
3. When UV finds this pattern, it:

- Parses the Python list between the markers
- Interprets each string as a package requirement (including version constraints)
- Creates a temporary virtual environment if needed
- Resolves all dependencies (including transitive ones)
- Installs them into the virtual environment
- Then executes your script in that environment

Here's an example of how the same script manifest could be more complex:

```python
# /// script
# dependencies = [
#   "pandas>=2.0.0",
#   "requests[security]>=2.31.0",
#   "rich[jupyter]>=13.7.0",
# ]
# python_version = ">=3.8"
# ///
```

