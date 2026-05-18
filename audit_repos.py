import subprocess
import os

repos = [
    "/home/barberb/ipfs_datasets_py",
    "/home/barberb/cookbook",
    "/home/barberb/HACC/ipfs_datasets_py",
    "/home/barberb/HACC/complaint-generator",
    "/home/barberb/HACC/ipfs_accelerate_py",
    "/home/barberb/HACC",
    "/home/barberb/211-AI",
    "/home/barberb/complaint-generator/Solana-Slop",
    "/home/barberb/complaint-generator",
    "/home/barberb/portland-laws.github.io/ipfs_datasets_py",
    "/home/barberb/portland-laws.github.io",
    "/home/barberb/logic-repair.0OzoH8/repo",
    "/home/barberb/municipal_scrape_workspace",
    "/home/barberb/Clarity_Act_Deontic_Logic",
    "/home/barberb/ipfs_kit_py",
    "/home/barberb/ipfs_accelerate_py"
]

def run(cmd, cwd=None):
    try:
        return subprocess.check_output(cmd, shell=True, cwd=cwd, stderr=subprocess.STDOUT).decode().strip()
    except subprocess.CalledProcessError as e:
        return e.output.decode().strip() if e.output else "ERROR"

for repo in repos:
    if not os.path.isdir(repo): continue
    print(f"\nREPO: {repo}")
    
    # Get default branch
    default_branch = run("git symbolic-ref --short refs/remotes/origin/HEAD", repo)
    if "ERROR" in default_branch:
        # Fallback
        remote_heads = run("git branch -r", repo)
        if "origin/main" in remote_heads: default_branch = "origin/main"
        elif "origin/master" in remote_heads: default_branch = "origin/master"
        else: default_branch = "origin/HEAD" # May still fail

    wt_list = run("git worktree list --porcelain", repo).split("\n\n")
    for wt_entry in wt_list:
        if not wt_entry.strip(): continue
        lines = wt_entry.strip().split("\n")
        info = {l.split(" ")[0]: " ".join(l.split(" ")[1:]) for l in lines}
        wt_path = info.get("worktree")
        if not wt_path: continue
        
        exists = os.path.isdir(wt_path)
        if not exists:
            print(f"  [STALE] {wt_path}")
            continue
            
        branch = run("git symbolic-ref --short -q HEAD || echo DETACHED", wt_path)
        dirty_count = run("git status --porcelain | wc -l", wt_path)
        is_dirty = dirty_count != "0"
        
        upstream = run("git rev-parse --abbrev-ref --symbolic-full-name @{u}", wt_path)
        ab = "N/A"
        if "ERROR" not in upstream:
            ab = run(f"git rev-list --left-right --count {upstream}...HEAD", wt_path)
        
        merged = "N/A"
        if "origin/" in default_branch and branch != "DETACHED":
            res = run(f"git merge-base --is-ancestor HEAD {default_branch}", wt_path)
            merged = "YES" if res == "" else "NO"
        
        status = "MAIN_WORKTREE_KEEP" if wt_path == repo else "UNKNOWN"
        if wt_path != repo:
            if is_dirty: status = "NEEDS_ATTENTION_DIRTY"
            elif merged == "YES": status = "SAFE_DELETE_NOW"
            elif branch == "DETACHED": status = "SAFE_DELETE_NOW" # Simplified
            else: status = "DELETE_AFTER_PUSH_OR_PR"

        print(f"  PATH: {wt_path} | BRANCH: {branch} | DIRTY: {is_dirty} | AB: {ab} | MERGED: {merged} | STATUS: {status}")
