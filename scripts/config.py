import os

# GitHub settings
GH_TOKEN = os.getenv("GH_TOKEN")
GH_USERNAME = os.getenv("GH_USERNAME") or "VANSH-THAPAR"

# LeetCode settings
LEETCODE_USERNAME = os.getenv("LEETCODE_USERNAME") or "vanshthapar"

# Personal info
NAME = "Vansh Thapar"
OCCUPATION = "Associate AI Engineer Intern"
COMPANY = "Lowe's India"
UNIVERSITY = "Chitkara University"
DEGREE = "B.E in Computer Science and Engineering"
COUNTRY = "India"
BIRTHDAY = "2005-08-14"
OS_LIST = ["Windows", "Linux"]

PROGRAMMING_LANGUAGES = ["C++", "Python", "JavaScript", "TypeScript", "SQL"]
LANGUAGES_SPOKEN = ["English", "Hindi", "Punjabi"]
EMAIL = "vanshthapar.professional@gmail.com"
PORTFOLIO = "Coming Soon"
LINKEDIN = "https://www.linkedin.com/in/vansh-thapar-345523324/"
HOBBIES = ["Building AI Products" ,"Problem Solving", "Astronomy", "Sports"]

# Theme definitions
THEMES = {
    "dark": {
        "bg_color": "#0d1117",
        "border_color": "#30363d",
        "title_bar_bg": "#161b22",
        "title_bar_fg": "#8b949e",
        "text_color": "#c9d1d9",
        "keyword_color": "#ff7b72",
        "string_color": "#a5d6ff",
        "prompt_color": "#79c0ff",
        "value_color": "#d2a8ff",
        "accent_color": "#2f81f7"
    },
    "light": {
        "bg_color": "#ffffff",
        "border_color": "#d0d7de",
        "title_bar_bg": "#f6f8fa",
        "title_bar_fg": "#57606a",
        "text_color": "#24292f",
        "keyword_color": "#cf222e",
        "string_color": "#0a3069",
        "prompt_color": "#0550ae",
        "value_color": "#8250df",
        "accent_color": "#0969da"
    }
}
