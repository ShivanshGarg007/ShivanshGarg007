import requests
import config
from utils import setup_logger

logger = setup_logger(__name__)

def fetch_leetcode_stats() -> dict:
    if not config.LEETCODE_USERNAME:
        logger.warning("LEETCODE_USERNAME not found. Returning default LeetCode stats.")
        return {
            "LC_RATING": "N/A", "LC_RANKING": "N/A", "LC_SOLVED": "N/A",
            "LC_EASY": "N/A", "LC_MEDIUM": "N/A", "LC_HARD": "N/A"
        }
        
    url = "https://leetcode.com/graphql"
    query = """
    query getUserProfile($username: String!) {
      matchedUser(username: $username) {
        profile {
          ranking
        }
        submitStats {
          acSubmissionNum {
            difficulty
            count
          }
        }
        userCalendar {
          submissionCalendar
        }
      }
      userContestRanking(username: $username) {
        rating
        globalRanking
      }
    }
    """
    try:
        response = requests.post(url, json={"query": query, "variables": {"username": config.LEETCODE_USERNAME}})
        response.raise_for_status()
        data = response.json()
        
        if "errors" in data:
            logger.error(f"GraphQL errors: {data['errors']}")
            raise Exception("GraphQL returned errors")
            
        data = data.get("data", {})
        matched_user = data.get("matchedUser", {}) or {}
        profile = matched_user.get("profile", {}) or {}
        submit_stats = matched_user.get("submitStats", {}).get("acSubmissionNum", [])
        
        contest = data.get("userContestRanking", {}) or {}
        
        
        import json
        calendar_str = matched_user.get("userCalendar", {}).get("submissionCalendar", "{}")
        try:
            cal_data = json.loads(calendar_str)
        except:
            cal_data = {}
            
        stats = {
            "LC_RATING": str(round(contest.get("rating", 0))) if contest.get("rating") else "N/A",
            "LC_RANKING": str(profile.get("ranking", "N/A")),
            "LC_SOLVED": "0",
            "LC_EASY": "0",
            "LC_MEDIUM": "0",
            "LC_HARD": "0",
            "LC_CALENDAR": cal_data
        }
        
        for item in submit_stats:
            diff = item.get("difficulty")
            count = item.get("count", 0)
            if diff == "All": stats["LC_SOLVED"] = str(count)
            elif diff == "Easy": stats["LC_EASY"] = str(count)
            elif diff == "Medium": stats["LC_MEDIUM"] = str(count)
            elif diff == "Hard": stats["LC_HARD"] = str(count)
            
        return stats
    except Exception as e:
        logger.error(f"Failed to fetch LeetCode stats: {e}")
        return {
            "LC_RATING": "N/A", "LC_RANKING": "N/A", "LC_SOLVED": "N/A",
            "LC_EASY": "N/A", "LC_MEDIUM": "N/A", "LC_HARD": "N/A",
            "LC_CALENDAR": {}
        }
