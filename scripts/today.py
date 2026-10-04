import os
import sys

# Ensure scripts directory is in path so we can run directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from github import fetch_github_stats
from leetcode import fetch_leetcode_stats
from renderer import ProfileRenderer
from utils import setup_logger

logger = setup_logger("today")

def main():
    logger.info("Starting profile generation...")
    
    # 1. Fetch stats
    logger.info("Fetching GitHub stats...")
    github_stats = fetch_github_stats()
    
    logger.info("Fetching LeetCode stats...")
    leetcode_stats = fetch_leetcode_stats()
    
    # 2. Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(base_dir, "assets")
    
    template_path = os.path.join(assets_dir, "template.svg")
    portrait_path = os.path.join(assets_dir, "portrait.svg")
    
    dark_output = os.path.join(assets_dir, "dark_mode.svg")
    light_output = os.path.join(assets_dir, "light_mode.svg")
    
    # 3. Render Profile SVG
    logger.info("Rendering profile SVGs...")
    renderer = ProfileRenderer(template_path, portrait_path)
    
    renderer.render(dark_output, "dark", github_stats, leetcode_stats)
    renderer.render(light_output, "light", github_stats, leetcode_stats)
    

    
    logger.info("Profile generation completed successfully!")

if __name__ == "__main__":
    main()