import subprocess
import sys
import traceback
from typing import List
import datetime
import os
import black

async def run_python_code(code: str, libraries: List[str], folder: str = "uploads", python_exec = sys.executable) -> dict:
    # Create a unique work directory per run
    work_dir = os.path.join(folder, "job_work")
    os.makedirs(work_dir, exist_ok=True)
    
    # Ensure the folder exists
    os.makedirs(folder, exist_ok=True)
    
    # File where we'll log execution results
    log_file_path = os.path.join(folder, "execution_result.txt")
    
    def log_to_file(content: str):
        """Append timestamped content to the log file."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"\n[{timestamp}]\n{content}\n{'-'*40}\n")
    
    # Get absolute path to avoid empty string issues
    abs_folder = os.path.abspath(folder)
    
    # Find project root - look for pyproject.toml, uv.lock, or use current directory
    current_dir = abs_folder
    project_root = None
    
    # Walk up the directory tree to find project root
    while current_dir != os.path.dirname(current_dir):  # Until we reach root directory
        if os.path.exists(os.path.join(current_dir, 'pyproject.toml')) or \
           os.path.exists(os.path.join(current_dir, 'uv.lock')) or \
           os.path.exists(os.path.join(current_dir, 'main.py')):  # Look for your main file
            project_root = current_dir
            break
        current_dir = os.path.dirname(current_dir)
    
    # Fallback to current working directory if no project root found
    if not project_root:
        project_root = os.getcwd()
        log_to_file(f"⚠️ Using current working directory as project root: {project_root}")
    else:
        log_to_file(f"✅ Found project root: {project_root}")
    
    # Step 1: Check & install required libraries using uv
    for lib in libraries:
        try:
            # Check if already installed
            check_cmd = [
                python_exec,
                "-c",
                f"import importlib.util, sys; "
                f"sys.exit(0) if importlib.util.find_spec('{lib}') else sys.exit(1)"
            ]
            result = subprocess.run(check_cmd, capture_output=True)
            
            if result.returncode != 0:  # not installed
                log_to_file(f"📦 Installing {lib} with uv in {project_root}...")
                
                # Use uv add command
                install_result = subprocess.run(
                    ["uv", "add", lib], 
                    cwd=project_root,
                    capture_output=True,
                    text=True
                )
                
                if install_result.returncode == 0:
                    log_to_file(f"✅ Successfully installed {lib}")
                else:
                    # Fallback to uv pip if uv add fails
                    log_to_file(f"⚠️ uv add failed, trying uv pip for {lib}...")
                    uv_pip_result = subprocess.run(
                        ["uv", "pip", "install", lib],
                        capture_output=True,
                        text=True,
                        cwd=project_root
                    )
                    if uv_pip_result.returncode != 0:
                        raise Exception(f"Both uv add and uv pip failed: {install_result.stderr} | {uv_pip_result.stderr}")
                    else:
                        log_to_file(f"✅ Successfully installed {lib} with uv pip")
            else:
                log_to_file(f"✅ {lib} already installed.")
                
        except Exception as install_error:
            error_message = f"❌ Failed to install library '{lib}':\n{install_error}"
            log_to_file(error_message)
            return {"code": 0, "output": error_message}
    
    # Step 2: Run the code
    try:
        try:
            code_formatted = black.format_str(code, mode=black.Mode())
        except Exception:
            code_formatted = code  # fallback if formatting fails
            
        log_to_file(f"📜 Executing Code:\n{code_formatted}")
        
        # Save code to job-specific file
        code_file_path = os.path.join(work_dir, "script.py")
        log_to_file(f"💾 Saving script to: {code_file_path}")
        
        with open(code_file_path, "w") as f:
            f.write(code)
        
        # Verify file was created
        if not os.path.exists(code_file_path):
            error_message = f"❌ Failed to create script file at {code_file_path}"
            log_to_file(error_message)
            return {"code": 0, "output": error_message}
        
        log_to_file(f"✅ Script saved successfully at: {code_file_path}")
        
        # Try uv run first, fallback to direct python execution
        try:
            # Run using uv run
            result = subprocess.run(
                ["uv", "run", "python", code_file_path],
                capture_output=True,
                text=True,
                cwd=project_root
            )
        except FileNotFoundError:
            # Fallback to direct python execution if uv is not available
            log_to_file("⚠️ uv not found, using direct python execution")
            result = subprocess.run(
                [python_exec, code_file_path],
                capture_output=True,
                text=True,
                cwd=project_root
            )
        
        if result.returncode == 0:
            success_message = f"✅ Code executed successfully:\n{result.stdout}"
            log_to_file(success_message)
            return {"code": 1, "output": result.stdout}
        else:
            error_message = f"❌ Execution error:\n{result.stderr}"
            log_to_file(error_message)
            return {"code": 0, "output": error_message}
            
    except Exception as e:
        error_details = f"❌ Error during code execution:\n{traceback.format_exc()}"
        log_to_file(error_details)
        return {"code": 0, "output": error_details}

