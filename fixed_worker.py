#!/usr/bin/env python3
import os
import json
import time
import shutil
import boto3
import subprocess
import traceback
import re
from datetime import datetime
from botocore.exceptions import ClientError

BASE = "/home/ubuntu/freecad_worker"

# Load configuration
with open(os.path.join(BASE, "config.json"), "r") as f:
    C = json.load(f)

BUCKET = C["bucket"]
REGION = C["region"]
INPUT_PREFIX = C.get("input_prefix", "input/")
OUTPUT_PREFIX = C.get("output_prefix", "output/")
LOGS_PREFIX = C.get("logs_prefix", "logs/")
PROCESSED_PREFIX = C.get("processed_prefix", "processed/")
CHECK_INTERVAL = int(C.get("check_interval_seconds", 15))
FREECAD_TIMEOUT = int(C.get("freecad_timeout_seconds", 300))

SUPPORTED_FORMATS = [".FCStd", ".STL", ".STEP", ".IGES", ".OBJ", ".GLTF"]

s3 = boto3.client("s3", region_name=REGION)

# ===============================================
#                   UTILITIES
# ===============================================
def log(msg):
    """Prints a log message."""
    print(f"[Worker] {msg}", flush=True)

def init_env():
    """Initializes the local directory structure."""
    for d in ["input", "output", "log"]:
        os.makedirs(os.path.join(BASE, d), exist_ok=True)
    log("Environment Initialized.")

def extract_version_from_filename(filename):
    """Extracts version number from filename like 'project-123_v2.py' -> 2"""
    match = re.search(r'_v(\d+)\.py$', filename)
    return int(match.group(1)) if match else 1

def get_project_name_from_filename(filename):
    """Extracts project name from filename like 'project-123_v2.py' -> 'project-123'"""
    return filename.replace('.py', '').rsplit('_v', 1)[0]

def list_projects():
    """Lists project folders in the S3 input prefix."""
    try:
        resp = s3.list_objects_v2(Bucket=BUCKET, Prefix=INPUT_PREFIX, Delimiter='/')
        prefixes = resp.get('CommonPrefixes', [])
        return [p['Prefix'].split('/')[-2] for p in prefixes]
    except Exception as e:
        log(f"list_projects error: {e}")
        return []

def mark_processed(project, filename):
    """Creates a .done file in S3 to mark a script as processed."""
    key = f"{PROCESSED_PREFIX}{project}/{filename}.done"
    s3.put_object(Bucket=BUCKET, Key=key, Body=b'')
    return

def is_processed(project, filename):
    """Checks if a .done file already exists for the given script."""
    key = f"{PROCESSED_PREFIX}{project}/{filename}.done"
    try:
        s3.head_object(Bucket=BUCKET, Key=key)
        return True
    except ClientError:
        return False

def upload_log(project, name, data, is_error=False):
    """Uploads a log file to S3."""
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    typ = "error" if is_error else "info"
    fname = f"{name}_{typ}_{ts}.log"
    local_log = os.path.join(BASE, "log", fname)
    with open(local_log, "w") as f:
        f.write(data)
    s3_key = f"{LOGS_PREFIX}{project}/{fname}"
    s3.upload_file(local_log, BUCKET, s3_key)
    log(f"Uploaded log to {s3_key}")

# ===============================================
#               FREECAD EXECUTION
# ===============================================
def run_freecad_script(local_script_path, output_dir, timeout):
    """Runs the FreeCAD script using freecadcmd with a specific output directory."""
    try:
        env = os.environ.copy()
        env["FREECAD_OUTPUT"] = output_dir
        cmd = ["freecadcmd", local_script_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"FreeCAD script timed out after {timeout} seconds.")
    except Exception as e:
        raise RuntimeError(f"Error running FreeCAD: {e}")

# ===============================================
#                 FILE PROCESSING
# ===============================================
def process_project(project):
    """Processes all .py files in a given project folder from S3."""
    prefix = f"{INPUT_PREFIX}{project}/"
    resp = s3.list_objects_v2(Bucket=BUCKET, Prefix=prefix)
    if "Contents" not in resp:
        return

    files = [obj['Key'] for obj in resp["Contents"] if obj['Key'].endswith(".py")]
    for key in files:
        filename = os.path.basename(key)
        if is_processed(project, filename):
            log(f"⏩ Skipping already processed script: {filename}")
            continue

        log(f"Processing {filename} in project {project}")

        local_input_dir = os.path.join(BASE, "input", project)
        os.makedirs(local_input_dir, exist_ok=True)

        local_script_path = os.path.join(local_input_dir, filename)
        s3.download_file(BUCKET, key, local_script_path)

        # Extract version number from filename (e.g., project-123_v2.py -> v2)
        version_num = extract_version_from_filename(filename)
        project_name = get_project_name_from_filename(filename)
        
        # Create version-based output folder (v1, v2, v3...)
        version_output_dir = os.path.join(BASE, "output", project, f"v{version_num}")
        os.makedirs(version_output_dir, exist_ok=True)

        try:
            out, err, code = run_freecad_script(local_script_path, version_output_dir, FREECAD_TIMEOUT)
            output = f"STDOUT:\n{out}\nSTDERR:\n{err}\nReturn code: {code}\n"
            upload_log(project, filename.replace('.py', ''), output, is_error=(code != 0))

            # Upload all supported output files with standardized names
            for root, _, files in os.walk(version_output_dir):
                for f in files:
                    file_ext = os.path.splitext(f)[1].upper()
                    if file_ext in [ext.upper() for ext in SUPPORTED_FORMATS]:
                        full_path = os.path.join(root, f)
                        
                        # Standardize filename: use project name + extension
                        # e.g., "Bottle.stl" -> "project-46021509.stl"
                        standardized_name = f"{project_name}{file_ext.lower()}"
                        
                        # S3 key: output/project-46021509/v2/project-46021509.stl
                        s3_key = f"{OUTPUT_PREFIX}{project}/v{version_num}/{standardized_name}"
                        
                        s3.upload_file(full_path, BUCKET, s3_key)
                        log(f"✅ Uploaded {s3_key} (original: {f})")

            if code == 0:
                mark_processed(project, filename)
                log(f"✅ Marked {filename} as processed.")
        except Exception as e:
            tb = traceback.format_exc()
            log(f"❌ Error while processing {filename}: {e}")
            upload_log(project, filename.replace('.py', ''), tb, is_error=True)
        finally:
            shutil.rmtree(local_input_dir, ignore_errors=True)
            shutil.rmtree(version_output_dir, ignore_errors=True)

# ===============================================
#                   MAIN LOOP
# ===============================================
def main():
    """The main loop for the worker process."""
    init_env()
    log("🚀 Worker started with standardized output structure.")
    while True:
        try:
            projects = list_projects()
            if not projects:
                log("No projects found.")
            for p in projects:
                process_project(p)
        except Exception as e:
            log(f"Main loop error: {e}")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
