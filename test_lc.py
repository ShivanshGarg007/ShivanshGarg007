import sys
import os
sys.path.append(os.path.abspath('scripts'))
import leetcode
import config

config.LEETCODE_USERNAME = "VANSHTHAPAR"
stats = leetcode.fetch_leetcode_stats()
print("Keys:", stats.keys())
if "LC_CALENDAR" in stats:
    print("Calendar size:", len(stats["LC_CALENDAR"]))
    items = list(stats["LC_CALENDAR"].items())
    print("First 5:", items[:5])
    print("Last 5:", items[-5:])
else:
    print("No LC_CALENDAR")
