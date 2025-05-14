from datetime import date
import os
from utils.uptime_calculator import calculate_uptime
from utils.github_stats import get_github_stats
from utils.svg_manager import SVGManager
from utils.config import setup_logger

logger = setup_logger("Main")

def main():
    try:
        file_paths = ['public/light_mode.svg', 'public/dark_mode.svg']
        logger.info("Calculating uptime...")
        uptime_data = calculate_uptime(date(2002, 11, 27))
        
        username = os.getenv('GITHUB_USERNAME', 'parthsolanke')
        logger.info(f"Fetching GitHub stats for {username}...")
        stats = get_github_stats(username)
        
        logger.info("Updating SVG files...")
        svg_manager = SVGManager(file_paths)
        svg_manager.update_uptime(uptime_data)
        svg_manager.update_github_stats(stats)
        logger.info("Successfully updated README files")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == '__main__':
    main()
