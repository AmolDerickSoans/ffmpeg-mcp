from mcp.server.fastmcp import FastMCP
import subprocess
import os

# Check if FastMCP is properly imported
print("FastMCP imported from:", FastMCP.__module__)

# Initialize the MCP server
try:
    mcp = FastMCP(
        name="FFmpegServer",
        description="A server for multimedia processing with FFmpeg",
        version="0.1.0"
    )
except Exception as e:
    print(f"Error initializing FastMCP: {e}")
    exit(1)

# Define working directory for security
WORKING_DIR = os.path.expanduser("~/ffmpeg_mcp_files")
os.makedirs(WORKING_DIR, exist_ok=True)

def is_safe_path(base_path: str, path: str) -> bool:
    """Ensure path stays within working directory"""
    abs_base = os.path.abspath(base_path)
    abs_path = os.path.abspath(path)
    return abs_path.startswith(abs_base)

def run_ffmpeg_command(command: list) -> dict:
    """Run FFmpeg command and return structured response"""
    try:
        # Get ffmpeg path from which command
        ffmpeg_path = subprocess.check_output(['which', 'ffmpeg']).decode().strip()
        # Replace the first element (ffmpeg) with the full path
        command[0] = ffmpeg_path
        
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        return {
            "success": True,
            "output": result.stdout.strip(),
            "error": None
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "output": None,
            "error": e.stderr.strip()
        }
    except Exception as e:
        return {
            "success": False,
            "output": None,
            "error": str(e)
        }

@mcp.tool()
def trim_video(input_path: str, start_time: float, duration: float, output_path: str) -> dict:
    """
    Trim a video to a specified start time and duration.
    """
    full_input_path = os.path.join(WORKING_DIR, input_path)
    full_output_path = os.path.join(WORKING_DIR, output_path)

    if not is_safe_path(WORKING_DIR, full_input_path) or not is_safe_path(WORKING_DIR, full_output_path):
        return {"success": False, "output": None, "error": "Path outside working directory not allowed"}
    
    if not os.path.exists(full_input_path):
        return {"success": False, "output": None, "error": f"Input file {input_path} does not exist"}
    
    if start_time < 0 or duration <= 0:
        return {"success": False, "output": None, "error": "Invalid time parameters"}

    command = [
        "ffmpeg",
        "-i", full_input_path,
        "-ss", str(start_time),
        "-t", str(duration),
        "-c:v", "copy",
        "-c:a", "copy",
        "-y",
        full_output_path
    ]
    result = run_ffmpeg_command(command)
    if result["success"]:
        result["output"] = f"Video trimmed to {full_output_path}"
    return result

@mcp.tool()
def convert_video_format(input_path: str, output_format: str, output_path: str) -> dict:
    """
    Convert a video to a specified format.
    """
    full_input_path = os.path.join(WORKING_DIR, input_path)
    full_output_path = os.path.join(WORKING_DIR, output_path)
    output_format = output_format.lower().strip()

    if not is_safe_path(WORKING_DIR, full_input_path) or not is_safe_path(WORKING_DIR, full_output_path):
        return {"success": False, "output": None, "error": "Path outside working directory not allowed"}
    
    if not os.path.exists(full_input_path):
        return {"success": False, "output": None, "error": f"Input file {input_path} does not exist"}
    
    if not full_output_path.endswith(f".{output_format}"):
        full_output_path = f"{full_output_path}.{output_format}"

    command = [
        "ffmpeg",
        "-i", full_input_path,
        "-f", output_format,
        "-y",
        full_output_path
    ]
    result = run_ffmpeg_command(command)
    if result["success"]:
        result["output"] = f"Video converted to {full_output_path}"
    return result

if __name__ == "__main__":
    print(f"Starting FFmpegServer - Working directory: {WORKING_DIR}")
    try:
        # Try different possible method names
        if hasattr(mcp, 'run'):
            mcp.run()
        elif hasattr(mcp, 'start'):
            print("Using start() instead of run()")
            mcp.start()
        elif hasattr(mcp, 'serve'):
            print("Using serve() instead of run()")
            mcp.serve()
        else:
            print("Available methods:", dir(mcp))
            raise AttributeError("No known start method found for FastMCP")
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Server object methods:", dir(mcp))