# Fill GitHub Contribution Graph
# Usage: python fill.py --days 365 --commits 15

import os
import sys
import random
import argparse
from datetime import datetime, timedelta
from subprocess import run, CalledProcessError

def check_git():
    try:
        run(["git", "--version"], check=True, capture_output=True)
    except (FileNotFoundError, CalledProcessError):
        print("Error: Git is not installed or not in system PATH.")
        sys.exit(1)

def get_git_email():
    try:
        result = run(["git", "config", "user.email"], check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except CalledProcessError:
        return None

def main():
    parser = argparse.ArgumentParser(description="Fill GitHub Contribution Graph with backdated commits.")
    parser.add_argument("-d", "--days", type=int, default=365, help="Number of days to go back (default: 365)")
    parser.add_argument("-c", "--commits", type=int, default=10, help="Maximum commits per day (default: 10)")
    parser.add_argument("-e", "--email", type=str, help="GitHub Email (overrides Git config)")
    parser.add_argument("-p", "--push", action="store_true", help="Force push changes to origin main after generating")
    args = parser.parse_args()

    check_git()

    email = args.email or get_git_email()
    if not email or "@example.com" in email:
        print("Error: Valid GitHub email is required.")
        print("Please configure Git or pass your email using the --email argument:")
        print("  python fill.py --email your_email@gmail.com")
        sys.exit(1)

    print("Git Email Configured:", email)
    
    # Initialize workspace git if not already
    if not os.path.exists(".git"):
        run(["git", "init", "-b", "main"], check=True)
        print("Initialized new local Git repository.")

    # Set local config
    run(["git", "config", "user.email", email], check=True)
    
    # Ensure README exists
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        with open(readme_path, "w") as f:
            f.write("# My Contributions\n\nAutomated activity log.\n")
        run(["git", "add", readme_path], check=True)
        run(["git", "commit", "-m", "Initial commit", "--date", (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d %H:%M:%S")], check=True)

    curr_date = datetime.now()
    start_date = curr_date - timedelta(days=args.days)
    
    print(f"Generating contributions from {start_date.strftime('%Y-%m-%d')} to today...")
    
    total_commits = 0
    for day_offset in range(args.days + 1):
        day = start_date + timedelta(days=day_offset)
        
        # Decide number of commits for this day (random up to max)
        daily_commits = random.randint(5, args.commits)
        
        # Generate random commit times between 9 AM (540 mins) and 9 PM (1260 mins)
        commit_minutes = sorted(random.randint(540, 1260) for _ in range(daily_commits))
        
        for minutes in commit_minutes:
            commit_time = day.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(minutes=minutes, seconds=random.randint(0, 59))
            
            # Skip future commits
            if commit_time > curr_date:
                continue
                
            formatted_date = commit_time.strftime("%Y-%m-%d %H:%M:%S")
            
            with open(readme_path, "a") as f:
                f.write(f"Contribution: {formatted_date}\n")
                
            # Use environmental variables to force both author and committer dates to match
            env = os.environ.copy()
            env["GIT_AUTHOR_DATE"] = formatted_date
            env["GIT_COMMITTER_DATE"] = formatted_date
            
            # Use -a to commit all tracked files in one go, avoiding extra git add processes
            run(["git", "commit", "-a", "-m", f"Contribution: {formatted_date}", "--date", formatted_date], env=env, check=True)
            total_commits += 1

        # Print progress and flush stdout so it is visible in logs in real-time
        if day_offset % 30 == 0 or day_offset == args.days:
            print(f"  Processed {day_offset}/{args.days} days... ({total_commits} commits created)", flush=True)

    print(f"Created {total_commits} backdated commits successfully!", flush=True)
    
    if args.push:
        print("Pushing to GitHub (origin main)...", flush=True)
        try:
            run(["git", "push", "-f", "origin", "main"], check=True)
            print("Pushed successfully! Your graph should update shortly.", flush=True)
        except CalledProcessError as e:
            print("Push failed. Make sure your remote origin is set up correctly:", flush=True)
            print("  git remote add origin <your-repo-url>", flush=True)

if __name__ == "__main__":
    main()
