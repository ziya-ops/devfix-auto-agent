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
            # Run Docker using subprocess (more reliable than deprecated docker SDK)
            cmd = [
                "docker", "run", "--rm",
                "-v", f"{temp_file}:/tmp/code.py",
                "-m", "512m",
                "--cpu-quota", "50000",
                "python:3.12-slim",
                "sh", "-c",
                "python -m pytest /tmp/code.py -q --tb=no"
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

            success = "1 passed" in output or ("passed" in output and "failed" not in output)
            return success, output

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