import subprocess

def clone_repo(repo_url, clone_path):
    try:
        result = subprocess.run(
            ['git', 'clone', repo_url, clone_path],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ Repo cloned to: {clone_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git clone failed:\n{e.stderr}")

# Example usage
if __name__ == "__main__":
    repo_url = "https://github.com/user/repo-name.git"  # Replace with actual repo URL
    clone_path = "/path/to/clone/location"              # Replace with desired local path

    clone_repo(repo_url, clone_path)
