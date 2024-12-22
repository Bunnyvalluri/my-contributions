import os
import sys
import random
import argparse
from datetime import datetime, timedelta
import subprocess

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--days", type=int, default=365, help="Number of days to go back")
    parser.add_argument("-c", "--commits", type=int, default=20, help="Maximum commits per day")
    parser.add_argument("-e", "--email", type=str, default="vallurirahul3@gmail.com", help="GitHub Email")
    parser.add_argument("-p", "--push", action="store_true", help="Force push changes to origin main")
    args = parser.parse_args()

    # Read existing files if they exist so we can include them in the git tree
    fill_py_content = b""
    if os.path.exists("fill.py"):
        with open("fill.py", "rb") as f:
            fill_py_content = f.read()
            
    fill_ps1_content = b""
    if os.path.exists("fill.ps1"):
        with open("fill.ps1", "rb") as f:
            fill_ps1_content = f.read()

    # We will read this file (fast_fill.py) contents as well
    fast_fill_py_content = b""
    try:
        with open(__file__, "rb") as f:
            fast_fill_py_content = f.read()
    except Exception:
        pass

    # We will generate commits starting from `days` ago up to today.
    curr_date = datetime.now()
    start_date = curr_date - timedelta(days=args.days)
    
    # Timezone offset for IST (UTC+5:30)
    tz_offset = "+0530"
    
    # Start git fast-import process
    proc = subprocess.Popen(
        ["git", "fast-import", "--force", "--quiet"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Initial readme lines
    readme_lines = ["# My Contributions", "", "Automated activity log."]
    total_commits = 0
    
    def write(data):
        proc.stdin.write(data)
        
    for day_offset in range(args.days + 1):
        day = start_date + timedelta(days=day_offset)
        
        # Generate between 10 and max commits to ensure dark green squares
        daily_commits = random.randint(10, args.commits)
        
        # Sort commit times to keep chronological ordering
        commit_minutes = sorted(random.randint(540, 1260) for _ in range(daily_commits))
        
        for minutes in commit_minutes:
            commit_time = day.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(minutes=minutes, seconds=random.randint(0, 59))
            if commit_time > curr_date:
                continue
                
            formatted_date = commit_time.strftime("%Y-%m-%d %H:%M:%S")
            epoch_seconds = int(commit_time.timestamp())
            
            readme_lines.append(f"Contribution: {formatted_date}")
            readme_content = "\n".join(readme_lines).encode("utf-8")
            
            commit_msg = f"Contribution: {formatted_date}".encode("utf-8")
            
            # Write commit block
            write(b"commit refs/heads/main\n")
            write(f"committer Bunnyvalluri <{args.email}> {epoch_seconds} {tz_offset}\n".encode("utf-8"))
            write(f"data {len(commit_msg)}\n".encode("utf-8"))
            write(commit_msg + b"\n")
            
            # Write files to the commit
            write(b"M 100644 inline README.md\n")
            write(f"data {len(readme_content)}\n".encode("utf-8"))
            write(readme_content + b"\n")
            
            # Write python and powershell scripts to preserve them in the history
            if total_commits == 0:
                if fill_py_content:
                    write(b"M 100644 inline fill.py\n")
                    write(f"data {len(fill_py_content)}\n".encode("utf-8"))
                    write(fill_py_content + b"\n")
                if fill_ps1_content:
                    write(b"M 100644 inline fill.ps1\n")
                    write(f"data {len(fill_ps1_content)}\n".encode("utf-8"))
                    write(fill_ps1_content + b"\n")
                if fast_fill_py_content:
                    write(b"M 100644 inline fast_fill.py\n")
                    write(f"data {len(fast_fill_py_content)}\n".encode("utf-8"))
                    write(fast_fill_py_content + b"\n")
                    
            total_commits += 1

    proc.stdin.close()
    stdout, stderr = proc.communicate()
    
    if proc.returncode != 0:
        print("Error during fast-import:")
        print(stderr.decode("utf-8"))
        sys.exit(1)
        
    print(f"Successfully generated {total_commits} commits locally in less than 2 seconds!")
    
    if args.push:
        print("Pushing to GitHub (origin main)...")
        res = subprocess.run(["git", "push", "-f", "origin", "main"])
        if res.returncode == 0:
            print("Successfully pushed to GitHub! Your profile should update shortly.")
        else:
            print("Push failed.")

if __name__ == "__main__":
    main()
