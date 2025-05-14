import os
import requests
import time
from xml.etree import ElementTree
from typing import Dict
from utils.config import setup_logger

logger = setup_logger("GithubStats")

def handle_rate_limit(response: requests.Response) -> bool:
    """Handle GitHub API rate limiting by waiting if necessary."""
    if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers:
        remaining = int(response.headers['X-RateLimit-Remaining'])
        if remaining == 0:
            reset_time = int(response.headers['X-RateLimit-Reset'])
            sleep_time = reset_time - time.time()
            if sleep_time > 0:
                logger.warning(f"Rate limit exceeded. Waiting {sleep_time:.0f} seconds...")
                time.sleep(sleep_time + 1)
                return True
    return False

def get_github_stats(username: str) -> Dict:
    stats = {
        'public_repos': 0,
        'followers': 0,
        'stars': 0,
        'commits': '0',
        'contributed': '0',
        'prs_merged': '0',
        'prs_merged_percentage': '0%'
    }
    
    try:
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-Stats-Bot'
        }
        if 'GITHUB_TOKEN' in os.environ:
            headers['Authorization'] = f"token {os.environ['GITHUB_TOKEN']}"
            logger.info("Using GitHub token for authentication")
        
        # Fetch basic user info with retry on rate limit
        for attempt in range(3):
            response = requests.get(f"https://api.github.com/users/{username}", headers=headers)
            if response.status_code == 200:
                break
            if handle_rate_limit(response):
                continue
            response.raise_for_status()
        
        data = response.json()
        stats['public_repos'] = data['public_repos']
        stats['followers'] = data['followers']
        
        # Fetch repository data with retry on rate limit
        for attempt in range(3):
            repos_response = requests.get(data['repos_url'], headers=headers)
            if repos_response.status_code == 200:
                break
            if handle_rate_limit(repos_response):
                continue
            repos_response.raise_for_status()
        
        repos_data = repos_response.json()
        stats['stars'] = sum(repo['stargazers_count'] for repo in repos_data)
        
        # Fetch additional stats from GitHub readme stats API
        stats_urls = [
            f"https://github-readme-stats.vercel.app/api?username={username}&include_all_commits=true",
            f"https://github-readme-stats.vercel.app/api?username={username}&show=prs_merged,prs_merged_percentage"
        ]
        
        for url in stats_urls:
            try:
                response = requests.get(url)
                response.raise_for_status()
                svg_content = ElementTree.fromstring(response.content)
                
                if "include_all_commits=true" in url:
                    commits_element = svg_content.find('.//{http://www.w3.org/2000/svg}text[@data-testid="commits"]')
                    if commits_element is not None:
                        stats['commits'] = commits_element.text
                    contributed_element = svg_content.find('.//{http://www.w3.org/2000/svg}text[@data-testid="contribs"]')
                    if contributed_element is not None:
                        stats['contributed'] = contributed_element.text
                else:
                    prs_merged_element = svg_content.find('.//{http://www.w3.org/2000/svg}text[@data-testid="prs_merged"]')
                    if prs_merged_element is not None:
                        stats['prs_merged'] = prs_merged_element.text
                    prs_percentage_element = svg_content.find('.//{http://www.w3.org/2000/svg}text[@data-testid="prs_merged_percentage"]')
                    if prs_percentage_element is not None:
                        stats['prs_merged_percentage'] = f"{prs_percentage_element.text[0:2]}%"
            except requests.exceptions.RequestException as e:
                logger.warning(f"Failed to fetch stats from {url}: {str(e)}")
        
        logger.info(f"Successfully fetched GitHub stats for user '{username}'")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching GitHub stats: {str(e)}")
    except (KeyError, ValueError, AttributeError) as e:
        logger.error(f"Error parsing GitHub stats: {str(e)}")
    
    return stats
