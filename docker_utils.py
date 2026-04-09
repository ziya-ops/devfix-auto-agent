import subprocess
import tempfile
import os

def execute_code_in_docker(code: str) -> tuple[bool, str]:
    """
    Execute code in a Docker container using subprocess.
    This approach is more reliable than the deprecated docker SDK.
    """
    try:
        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            # Run Docker using subprocess with pytest installed
            cmd = [
                "docker", "run", "--rm",
                "-v", f"{temp_file}:/tmp/code.py",
                "-m", "512m",
                "--cpu-quota", "50000",
                "python:3.12-slim",
                "sh", "-c",
                "pip install pytest -q && python -m pytest /tmp/code.py -q --tb=no"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout.strip()
            if result.stderr:
                output += "\n" + result.stderr.strip()

            # Filter out gRPC warnings
            output_lines = [line for line in output.split('\n')
                          if 'ev_poll_posix.cc' not in line and 'FD from fork parent' not in line]
            clean_output = '\n'.join(output_lines).strip()

            success = "1 passed" in clean_output or ("passed" in clean_output and "failed" not in clean_output)
            return success, clean_output

        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    except subprocess.TimeoutExpired:
        return False, "Execution timeout (30s)"
    except FileNotFoundError:
        return False, "Docker not found. Please ensure Docker is installed and running."
    except Exception as e:
        return False, str(e)