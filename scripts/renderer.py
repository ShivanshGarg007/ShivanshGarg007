import os
import re
import math
import time
import config
from datetime import date
from dateutil.relativedelta import relativedelta
from utils import calculate_age, setup_logger

logger = setup_logger(__name__)

class LayoutConstants:
    CANVAS_WIDTH = 1600
    PORTRAIT_WIDTH = 630
    LINE_HEIGHT = 26
    CHAR_WIDTH = 9.5
    FONT_SIZE = 16

class SVGTextBuilder:
    def __init__(self, x=0, y=0, max_width=1000, line_height=26, char_width=9.5):
        self.x = x
        self.y = y
        self.max_width = max_width
        self.line_height = line_height
        self.char_width = char_width
        self.lines = []
        
    def add_line(self, content):
        self.y += self.line_height
        self.lines.append(f'<tspan x="{self.x}" y="{self.y}">{content}</tspan>')
        
    def add_empty_line(self):
        self.y += self.line_height

    def build(self):
        return "\n".join(self.lines)

    def kv_line(self, key, value, indent=20, is_last=False, is_string=True, value_class="string"):
        comma = "" if is_last else ","
        val_str = f'"{value}"' if is_string else str(value)
        
        max_chars = int((self.max_width - indent - len(key) - 10) / self.char_width)
        if len(val_str) > max_chars and max_chars > 3:
            val_str = val_str[:max_chars-3] + "..."
            if is_string:
                val_str += '"'
                
        return f'<tspan x="{self.x + indent}" class="keyword">"{key}"</tspan><tspan class="text">: </tspan><tspan class="{value_class}">{val_str}</tspan><tspan class="text">{comma}</tspan>'

    def wrap_array(self, key, items, indent=20, is_last=False):
        lines = []
        lines.append(f'<tspan x="{self.x + indent}" class="keyword">"{key}"</tspan><tspan class="text">: [</tspan>')
        max_chars = int((self.max_width - indent - 40) / self.char_width)
        
        current_line = []
        current_len = 0
        chunks = []
        for item in items:
            if current_len + len(item) + 4 > max_chars and current_line:
                chunks.append(current_line)
                current_line = [item]
                current_len = len(item)
            else:
                current_line.append(item)
                current_len += len(item) + 4
        if current_line:
            chunks.append(current_line)
            
        for i, chunk in enumerate(chunks):
            chunk_str = '"' + '", "'.join(chunk) + '"'
            if i < len(chunks) - 1:
                chunk_str += ","
            lines.append(f'<tspan x="{self.x + indent + 20}" class="value">{chunk_str}</tspan>')
            
        comma = "" if is_last else ","
        lines.append(f'<tspan x="{self.x + indent}" class="text">]{comma}</tspan>')
        return lines

def render_box(x, y, w, h, title):
    return f'''
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" class="pane-border"/>
    <rect x="{x + 15}" y="{y - 10}" width="{len(title)*9.5 + 20}" height="20" class="window" />
    <text x="{x + 25}" y="{y + 5}" class="pane-title">{title}</text>
    '''

class ProfileRenderer:
    def __init__(self, template_path: str, portrait_path: str = None):
        self.template_path = template_path
        self.portrait_path = portrait_path
        self.template_content = ""
        self.portrait_content = ""
        self.load_files()

    def load_files(self):
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                self.template_content = f.read()
            if self.portrait_path and os.path.exists(self.portrait_path):
                with open(self.portrait_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    content = re.sub(r'<\?xml.*?\?>', '', content)
                    content = re.sub(r'<!DOCTYPE.*?>', '', content)
                    self.portrait_content = content.strip()
        except Exception as e:
            logger.error(f"Failed to load SVG files: {e}")
            raise
            
    def render_heatmap(self, cal_data, start_x, start_y, max_width):
        if not cal_data:
            return f'<text x="{start_x + (max_width/2)}" y="{start_y + 40}" class="text text-dim" font-size="16" text-anchor="middle">No submission data available</text>', 80
            
        box_size = 15
        gap = 5
        rows = 7
        cols = 52
        
        from datetime import datetime, timedelta
        
        heatmap_width = cols * (box_size + gap)
        offset_x = start_x + (max_width - heatmap_width) / 2 + 20
        
        today = datetime.now()
        start_date = today - timedelta(days=cols * 7 - 1)
        
        svg_rects = []
        
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        current_month = -1
        
        for col in range(cols):
            target_date = start_date + timedelta(days=col * 7)
            month_idx = target_date.month - 1
            if month_idx != current_month:
                if col < cols - 2:
                    svg_rects.append(f'<text x="{offset_x + col * (box_size + gap)}" y="{start_y - 10}" class="text text-dim" font-size="13">{month_names[month_idx]}</text>')
                current_month = month_idx

        svg_rects.append(f'<text x="{offset_x - 35}" y="{start_y + (box_size + gap) * 1 + 12}" class="text text-dim" font-size="13">Mon</text>')
        svg_rects.append(f'<text x="{offset_x - 35}" y="{start_y + (box_size + gap) * 3 + 12}" class="text text-dim" font-size="13">Wed</text>')
        svg_rects.append(f'<text x="{offset_x - 35}" y="{start_y + (box_size + gap) * 5 + 12}" class="text text-dim" font-size="13">Fri</text>')

        for col in range(cols):
            for row in range(rows):
                day_offset = (col * 7 + row)
                target_date = start_date + timedelta(days=day_offset)
                target_timestamp = target_date.timestamp()
                
                count = 0
                for ts, c in cal_data.items():
                    if abs(int(ts) - target_timestamp) < 86400:
                        count += c
                        
                level = 0
                if count > 10: level = 4
                elif count > 5: level = 3
                elif count > 2: level = 2
                elif count > 0: level = 1
                
                level_var = f"{{{{LC_HEATMAP_L{level}}}}}"
                x_pos = offset_x + col * (box_size + gap)
                y_pos = start_y + row * (box_size + gap)
                svg_rects.append(f'<rect x="{x_pos}" y="{y_pos}" width="{box_size}" height="{box_size}" rx="4" fill="{level_var}" />')
        
        legend_y = start_y + rows * (box_size + gap) + 20
        legend_x = offset_x + heatmap_width - 160
        svg_rects.append(f'<text x="{legend_x - 45}" y="{legend_y + 12}" class="text text-dim" font-size="13">Less</text>')
        for i in range(5):
            lx = legend_x + i * (box_size + gap)
            level_var = f"{{{{LC_HEATMAP_L{i}}}}}"
            svg_rects.append(f'<rect x="{lx}" y="{legend_y}" width="{box_size}" height="{box_size}" rx="3" fill="{level_var}" />')
        svg_rects.append(f'<text x="{legend_x + 5 * (box_size + gap) + 10}" y="{legend_y + 12}" class="text text-dim" font-size="13">More</text>')
                
        return "\n".join(svg_rects), (rows * (box_size + gap) + 50)

    def render(self, output_path: str, theme_name: str, github_stats: dict, leetcode_stats: dict):
        content = self.template_content
        if "{{CONTENT}}" not in content:
            raise ValueError("CRITICAL ERROR: Placeholder {{CONTENT}} is missing from template.svg!")
            
        theme = config.THEMES.get(theme_name, config.THEMES["dark"])
        svg_parts = []
        current_y = 80
        
        # 1. PROFILE SECTION (whoami, uptime, cat config, and portrait on left)
        portrait_x = 40
        portrait_y = current_y
        portrait_end_y = current_y
        portrait_svg = ""
        
        if self.portrait_path and self.portrait_content:
            try:
                import xml.etree.ElementTree as ET
                tree = ET.fromstring(self.portrait_content)
                orig_w = float(tree.get('width', '1254').replace('px','').replace('%',''))
                orig_h = float(tree.get('height', '1254').replace('px','').replace('%',''))
                scale = LayoutConstants.PORTRAIT_WIDTH / orig_w
                portrait_actual_h = orig_h * scale
                
                match = re.search(r'<svg[^>]*>', self.portrait_content)
                if match:
                    inner = self.portrait_content[match.end():self.portrait_content.rfind('</svg>')].strip()
                    prompt = f'<text x="{portrait_x}" y="{portrait_y + 16}" class="text"><tspan class="prompt">vansh@thapar:~$</tspan> neofetch</text>'
                    g = f'<g transform="translate({portrait_x},{portrait_y + 40}) scale({scale})">{inner}</g>'
                    portrait_svg = f"{prompt}\n{g}"
                    portrait_end_y = portrait_y + 40 + portrait_actual_h
            except Exception as e:
                logger.error(f"Failed to process portrait: {e}")
                
        profile_x = 700
        profile_y = current_y - LayoutConstants.LINE_HEIGHT
        builder = SVGTextBuilder(x=profile_x, y=profile_y, max_width=860)
        
        builder.add_line('<tspan class="prompt">vansh@thapar:~$</tspan><tspan class="text"> whoami</tspan>')
        builder.add_line(f'<tspan class="value">{config.NAME}</tspan>')
        builder.add_line(f'<tspan class="text">{config.OCCUPATION} @ {config.COMPANY}</tspan>')
        builder.add_line(f'<tspan class="text">{config.DEGREE}</tspan>')
        builder.add_line(f'<tspan class="text">{config.COUNTRY}</tspan>')
        builder.add_empty_line()
        
        builder.add_line('<tspan class="prompt">vansh@thapar:~$</tspan><tspan class="text"> uptime</tspan>')
        builder.add_line(f'<tspan class="value">{calculate_age()}</tspan>')
        builder.add_empty_line()
        
        builder.add_line('<tspan class="prompt">vansh@thapar:~$</tspan><tspan class="text"> cat ~/.config/profile.json</tspan>')
        builder.add_line('<tspan class="text">{</tspan>')
        builder.add_line(builder.kv_line("name", config.NAME))
        builder.add_line(builder.kv_line("role", config.OCCUPATION))
        builder.add_line(builder.kv_line("organization", config.COMPANY))
        builder.add_line(builder.kv_line("education", config.DEGREE))
        builder.add_line(builder.kv_line("location", config.COUNTRY))
        builder.add_line(builder.kv_line("uptime", calculate_age()))
        for line in builder.wrap_array("specialization", ["Full Stack", "AI / ML", "Cloud"]):
            builder.add_line(line)
        for line in builder.wrap_array("toolbox", config.PROGRAMMING_LANGUAGES):
            builder.add_line(line)
        builder.add_line(builder.kv_line("currently_building", "Scalable AI-powered applications"))
        builder.add_line(builder.kv_line("status", "Always shipping."))
        
        builder.add_line(f'<tspan x="{builder.x + 20}" class="keyword">"contact"</tspan><tspan class="text">: {{</tspan>')
        builder.add_line(builder.kv_line("email", config.EMAIL, indent=40))
        builder.add_line(builder.kv_line("linkedin", config.LINKEDIN, indent=40, is_last=True))
        builder.add_line(f'<tspan x="{builder.x + 20}" class="text">}}</tspan>')
        builder.add_line('<tspan class="text">}</tspan>')
        
        profile_end_y = builder.y
        svg_parts.append(portrait_svg)
        svg_parts.append(f'<text class="text">\n{builder.build()}\n</text>')
        
        current_y = max(portrait_end_y, profile_end_y) + 60
        
        # 2. GITHUB DASHBOARD
        gh_builder = SVGTextBuilder(x=40, y=current_y - LayoutConstants.LINE_HEIGHT, max_width=1520)
        gh_builder.add_line('<tspan class="prompt">vansh@thapar:~$</tspan><tspan class="text"> github</tspan>')
        svg_parts.append(f'<text class="text">\n{gh_builder.build()}\n</text>')
        current_y = gh_builder.y + 30
        
        gh_box_h = 160
        svg_parts.append(render_box(40, current_y, 480, gh_box_h, "Repository Overview"))
        svg_parts.append(f'<text x="60" y="{current_y + 45}" class="text">Stars:      <tspan class="value">{github_stats.get("STARS", 0)}</tspan></text>')
        svg_parts.append(f'<text x="60" y="{current_y + 85}" class="text">Repos:      <tspan class="value">{github_stats.get("REPOS", 0)}</tspan></text>')
        svg_parts.append(f'<text x="60" y="{current_y + 125}" class="text">Followers:  <tspan class="value">{github_stats.get("FOLLOWERS", 0)}</tspan></text>')
        
        svg_parts.append(render_box(540, current_y, 560, gh_box_h, "Contribution Activity"))
        contribs = int(github_stats.get("CONTRIBUTIONS", 0))
        commits = int(github_stats.get("COMMITS", 0))
        bar_w = 340
        c_pct = min(1, contribs / max(1, 2000)) * bar_w
        svg_parts.append(f'<text x="560" y="{current_y + 60}" class="text">Contributions</text>')
        svg_parts.append(f'<rect x="710" y="{current_y + 50}" width="{bar_w}" height="10" rx="3" class="chart-bar-bg" />')
        svg_parts.append(f'<rect x="710" y="{current_y + 50}" width="{c_pct}" height="10" rx="3" class="chart-bar-fg" />')
        svg_parts.append(f'<text x="{710 + bar_w + 10}" y="{current_y + 60}" class="text value" font-size="14">{contribs}</text>')
        
        com_pct = min(1, commits / max(1, 1000)) * bar_w
        svg_parts.append(f'<text x="560" y="{current_y + 110}" class="text">Commits</text>')
        svg_parts.append(f'<rect x="710" y="{current_y + 100}" width="{bar_w}" height="10" rx="3" class="chart-bar-bg" />')
        svg_parts.append(f'<rect x="710" y="{current_y + 100}" width="{com_pct}" height="10" rx="3" class="chart-bar-fg" />')
        svg_parts.append(f'<text x="{710 + bar_w + 10}" y="{current_y + 110}" class="text value" font-size="14">{commits}</text>')
        
        svg_parts.append(render_box(1120, current_y, 440, gh_box_h, "System Status"))
        svg_parts.append(f'<text x="1140" y="{current_y + 60}" class="text keyword">SYSTEM HEALTH: OPTIMAL</text>')
        svg_parts.append(f'<text x="1140" y="{current_y + 100}" class="text text-dim">Syncing daily with GitHub API...</text>')
        
        current_y += gh_box_h + 60
        
        # 3. LEETCODE DASHBOARD
        lc_builder = SVGTextBuilder(x=40, y=current_y - LayoutConstants.LINE_HEIGHT, max_width=1520)
        lc_builder.add_line('<tspan class="prompt">vansh@thapar:~$</tspan><tspan class="text"> leetcode</tspan>')
        svg_parts.append(f'<text class="text">\n{lc_builder.build()}\n</text>')
        current_y = lc_builder.y + 30
        
        lc_box_y = current_y
        lc_cy = current_y + 40
        lc_box_index = len(svg_parts)
        
        # Content inside box
        total = int(leetcode_stats.get("LC_SOLVED", 0))
        svg_parts.append(f'<text x="60" y="{lc_cy}" class="text keyword">User: <tspan class="value">{config.LEETCODE_USERNAME}</tspan></text>')
        svg_parts.append(f'<text x="360" y="{lc_cy}" class="text keyword">Rank: <tspan class="value">{leetcode_stats.get("LC_RANKING", "N/A")}</tspan></text>')
        svg_parts.append(f'<text x="660" y="{lc_cy}" class="text keyword">Rating: <tspan class="value">{leetcode_stats.get("LC_RATING", "N/A")}</tspan></text>')
        svg_parts.append(f'<text x="960" y="{lc_cy}" class="text keyword">Total Solved: <tspan class="value">{total}</tspan></text>')
        
        lc_cy += 120
        easy = int(leetcode_stats.get("LC_EASY", 0))
        med = int(leetcode_stats.get("LC_MEDIUM", 0))
        hard = int(leetcode_stats.get("LC_HARD", 0))
        
        # --- DONUT CHART ---
        donut_cx = 310
        donut_cy = lc_cy
        donut_r = 75
        donut_thickness = 22
        
        import math
        circumference = 2 * math.pi * donut_r
        
        # Background track
        svg_parts.append(f'<circle cx="{donut_cx}" cy="{donut_cy}" r="{donut_r}" fill="transparent" class="chart-bar-bg" stroke-width="{donut_thickness}" />')
        
        if total > 0:
            e_pct = easy / total
            m_pct = med / total
            h_pct = hard / total
            
            e_len = e_pct * circumference
            m_len = m_pct * circumference
            h_len = h_pct * circumference
            
            # Draw segments (Easy -> Medium -> Hard)
            svg_parts.append(f'<circle cx="{donut_cx}" cy="{donut_cy}" r="{donut_r}" fill="transparent" stroke="#00b8a3" stroke-width="{donut_thickness}" stroke-dasharray="{e_len} {circumference}" stroke-dashoffset="0" transform="rotate(-90 {donut_cx} {donut_cy})" />')
            svg_parts.append(f'<circle cx="{donut_cx}" cy="{donut_cy}" r="{donut_r}" fill="transparent" stroke="#ffc01e" stroke-width="{donut_thickness}" stroke-dasharray="{m_len} {circumference}" stroke-dashoffset="-{e_len}" transform="rotate(-90 {donut_cx} {donut_cy})" />')
            svg_parts.append(f'<circle cx="{donut_cx}" cy="{donut_cy}" r="{donut_r}" fill="transparent" stroke="#ef4743" stroke-width="{donut_thickness}" stroke-dasharray="{h_len} {circumference}" stroke-dashoffset="-{e_len + m_len}" transform="rotate(-90 {donut_cx} {donut_cy})" />')
        
        # Donut Center Text
        svg_parts.append(f'<text x="{donut_cx}" y="{donut_cy - 5}" class="text value" font-size="32" font-weight="bold" text-anchor="middle">{total}</text>')
        svg_parts.append(f'<text x="{donut_cx}" y="{donut_cy + 20}" class="text text-dim" font-size="14" text-anchor="middle">Solved</text>')
        
        # --- STATS LEGEND ---
        def draw_legend_item(x, y, label, val, total_val, color):
            pct = (val / max(1, total_val)) * 100
            return f'''
            <rect x="{x}" y="{y}" width="280" height="70" rx="8" class="pane-border" style="stroke: {color}; stroke-opacity: 0.2;" />
            <rect x="{x}" y="{y}" width="280" height="70" rx="8" fill="{color}" fill-opacity="0.05" />
            <circle cx="{x + 25}" cy="{y + 35}" r="8" fill="{color}" />
            <text x="{x + 45}" y="{y + 31}" class="text" font-size="16" fill="{color}" font-weight="600">{label}</text>
            <text x="{x + 45}" y="{y + 51}" class="text text-dim" font-size="13">{pct:.1f}%</text>
            <text x="{x + 260}" y="{y + 42}" class="text value" font-size="24" text-anchor="end" font-weight="bold">{val}</text>
            '''
        
        legend_y = lc_cy - 35
        svg_parts.append(draw_legend_item(470, legend_y, "Easy", easy, total, "#00b8a3"))
        svg_parts.append(draw_legend_item(790, legend_y, "Medium", med, total, "#ffc01e"))
        svg_parts.append(draw_legend_item(1110, legend_y, "Hard", hard, total, "#ef4743"))
        
        lc_cy += 120
        svg_parts.append(f'<text x="60" y="{lc_cy}" class="pane-title">Submission Calendar</text>')
        lc_cy += 30
        cal_data = leetcode_stats.get("LC_CALENDAR", {})
        heatmap_svg, hm_height = self.render_heatmap(cal_data, 60, lc_cy, 1480)
        svg_parts.append(heatmap_svg)
        
        lc_cy += hm_height
        lc_box_h = lc_cy - lc_box_y
        svg_parts.insert(lc_box_index, render_box(40, lc_box_y, 1520, lc_box_h, "LeetCode Analytics"))
        
        current_y = lc_box_y + lc_box_h + 60
        
        # 4. EXIT
        exit_builder = SVGTextBuilder(x=40, y=current_y - LayoutConstants.LINE_HEIGHT, max_width=1520)
        exit_builder.add_line('<tspan class="prompt">vansh@thapar:~$</tspan><tspan class="text"> exit</tspan>')
        exit_builder.add_line('<tspan class="text text-dim">logout</tspan>')
        exit_builder.add_line('<tspan class="text text-dim">Session terminated.</tspan>')
        svg_parts.append(f'<text class="text">\n{exit_builder.build()}\n</text>')
        
        current_y = exit_builder.y + 60
        
        content = content.replace("{{CANVAS_HEIGHT}}", str(int(current_y)))
        content = content.replace("{{CONTENT}}", "\n".join(svg_parts))
        
        for k, v in theme.items():
            content = content.replace(f"{{{{{k.upper()}}}}}", v)
            
        if theme_name == "dark":
            content = content.replace("{{LC_HEATMAP_L0}}", theme.get("border_color", "#30363d"))
            content = content.replace("{{LC_HEATMAP_L1}}", "#0e4429")
            content = content.replace("{{LC_HEATMAP_L2}}", "#006d32")
            content = content.replace("{{LC_HEATMAP_L3}}", "#26a641")
            content = content.replace("{{LC_HEATMAP_L4}}", "#39d353")
        else:
            content = content.replace("{{LC_HEATMAP_L0}}", "#ebedf0")
            content = content.replace("{{LC_HEATMAP_L1}}", "#9be9a8")
            content = content.replace("{{LC_HEATMAP_L2}}", "#40c463")
            content = content.replace("{{LC_HEATMAP_L3}}", "#30a14e")
            content = content.replace("{{LC_HEATMAP_L4}}", "#216e39")
        
        logger.info(f"Placeholder replacement success for {theme_name} mode. Dynamic Canvas Height: {int(current_y)}")
            
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Final output path: {output_path}")
        except Exception as e:
            logger.error(f"Failed to write SVG to {output_path}: {e}")
