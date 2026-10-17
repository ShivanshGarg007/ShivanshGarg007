import requests
import config
from utils import setup_logger

logger = setup_logger(__name__)

def fetch_github_stats() -> dict:
    if not config.GH_TOKEN or not config.GH_USERNAME:
        logger.warning("GH_TOKEN or GH_USERNAME not found. Returning default GitHub stats.")
        return {
            "FOLLOWERS": "0", "FOLLOWING": "0", "REPOS": "0",
            "STARS": "0", "COMMITS": "0", "CONTRIBUTIONS": "0",
            "ISSUES": "0", "PRS": "0"
        }

    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {config.GH_TOKEN}"}
    
    query = """
    query($login: String!) {
      user(login: $login) {
        followers { totalCount }
        following { totalCount }
        repositories(ownerAffiliations: OWNER) {
          totalCount
        }
        starredRepositories { totalCount }
        issues { totalCount }
        pullRequests { totalCount }
        contributionsCollection {
          contributionCalendar {
            totalContributions
          }
          totalCommitContributions
        }
      }
    }
    """
    try:
        response = requests.post(url, json={"query": query, "variables": {"login": config.GH_USERNAME}}, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if "errors" in data:
            logger.error(f"GraphQL errors: {data['errors']}")
            raise Exception("GraphQL returned errors")
            
        user_data = data.get("data", {}).get("user", {})
        if not user_data:
            logger.warning("No user data found for GitHub username.")
            raise Exception("No user data")
            
        contributions = user_data.get("contributionsCollection", {})
        
        return {
            "FOLLOWERS": str(user_data.get("followers", {}).get("totalCount", 0)),
            "FOLLOWING": str(user_data.get("following", {}).get("totalCount", 0)),
            "REPOS": str(user_data.get("repositories", {}).get("totalCount", 0)),
            "STARS": str(user_data.get("starredRepositories", {}).get("totalCount", 0)),
            "ISSUES": str(user_data.get("issues", {}).get("totalCount", 0)),
            "PRS": str(user_data.get("pullRequests", {}).get("totalCount", 0)),
            "CONTRIBUTIONS": str(contributions.get("contributionCalendar", {}).get("totalContributions", 0)),
            "COMMITS": str(contributions.get("totalCommitContributions", 0))
        }
    except Exception as e:
        logger.error(f"Failed to fetch GitHub stats: {e}")
        return {
            "FOLLOWERS": "N/A", "FOLLOWING": "N/A", "REPOS": "N/A",
            "STARS": "N/A", "COMMITS": "N/A", "CONTRIBUTIONS": "N/A",
            "ISSUES": "N/A", "PRS": "N/A"
        }
