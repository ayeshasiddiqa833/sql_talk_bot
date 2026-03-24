import streamlit as st
import tempfile
import os
from agent import build_agent, query_agent
from converter import convert_to_sqlite, is_supported, get_file_label, SUPPORTED_TYPES

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SQL Talk Bot",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme ─────────────────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

is_dark = st.session_state.theme == "dark"

THEMES = {
    "dark": {
        "bg_app":           "#0b0d14",
        "bg_sidebar":       "#0f1220",
        "bg_card":          "#131620",
        "bg_user_msg":      "#161b2e",
        "bg_bot_msg":       "#0e1a1f",
        "bg_sql":           "#090f1c",
        "bg_schema":        "#0f1520",
        "bg_input":         "#161b2e",
        "bg_button":        "#161b2e",
        "bg_expander":      "#111824",
        "bg_info":          "#0e1a2e",
        "bg_stat":          "#131a2a",
        "bg_thinking":      "#0e1520",
        "accent_user":      "#7c6af7",
        "accent_bot":       "#2dd4a7",
        "accent_warm":      "#f59e42",
        "border_sql":       "#1e3a5f",
        "border_schema":    "#1a2840",
        "border_button":    "#252f45",
        "border_divider":   "#1a2235",
        "border_card":      "#1e2640",
        "border_info":      "#1e3a5f",
        "font_heading":     "#eaecff",
        "font_subheading":  "#8a96c0",
        "font_primary":     "#d0d6f0",
        "font_user_msg":    "#c8cef0",
        "font_bot_msg":     "#90f0d8",
        "font_sql":         "#72c8ff",
        "font_schema":      "#68a8d4",
        "font_sidebar":     "#8898be",
        "font_muted":       "#445068",
        "font_empty":       "#2e3a54",
        "font_button":      "#a0b8d8",
        "font_toggle":      "#f0c060",
        "font_badge":       "#506080",
        "font_tip":         "#506888",
        "font_code":        "#72c8ff",
        "font_label":       "#6878a0",
        "font_info":        "#4a88c0",
        "font_stat_val":    "#2dd4a7",
        "font_stat_lbl":    "#3a5878",
        "font_thinking":    "#5a78a0",
        "font_ls_on":       "#2dd4a7",
        "font_ls_off":      "#556080",
        "toggle_bg":        "#161b2e",
        "toggle_border":    "#252f45",
        "tag_bg":           "#152238",
        "tag_color":        "#4a8ac8",
        "shadow":           "rgba(0,0,0,0.4)",
    },
    "light": {
        "bg_app":           "#f2f4fc",
        "bg_sidebar":       "#e8ecf8",
        "bg_card":          "#ffffff",
        "bg_user_msg":      "#ede9ff",
        "bg_bot_msg":       "#e0f8f2",
        "bg_sql":           "#dbeeff",
        "bg_schema":        "#e8eef8",
        "bg_input":         "#ffffff",
        "bg_button":        "#ffffff",
        "bg_expander":      "#f0f3fc",
        "bg_info":          "#eef5ff",
        "bg_stat":          "#f4f8ff",
        "bg_thinking":      "#f0f6ff",
        "accent_user":      "#6c56f5",
        "accent_bot":       "#0da87e",
        "accent_warm":      "#e07820",
        "border_sql":       "#90c4e8",
        "border_schema":    "#b0c8e8",
        "border_button":    "#c8d4ec",
        "border_divider":   "#d0d8f0",
        "border_card":      "#dce4f4",
        "border_info":      "#90c4e8",
        "font_heading":     "#0c1030",
        "font_subheading":  "#344070",
        "font_primary":     "#1c2448",
        "font_user_msg":    "#2a1a70",
        "font_bot_msg":     "#064038",
        "font_sql":         "#0a4890",
        "font_schema":      "#184870",
        "font_sidebar":     "#2a3860",
        "font_muted":       "#7080a0",
        "font_empty":       "#8090b8",
        "font_button":      "#283868",
        "font_toggle":      "#283868",
        "font_badge":       "#7080a0",
        "font_tip":         "#4a5880",
        "font_code":        "#0a4890",
        "font_label":       "#485878",
        "font_info":        "#1a58a8",
        "font_stat_val":    "#0a8870",
        "font_stat_lbl":    "#5878a0",
        "font_thinking":    "#4868a0",
        "font_ls_on":       "#0a8870",
        "font_ls_off":      "#8898b8",
        "toggle_bg":        "#ffffff",
        "toggle_border":    "#b8c8e8",
        "tag_bg":           "#dbeeff",
        "tag_color":        "#1a58a0",
        "shadow":           "rgba(100,120,200,0.08)",
    }
}

T            = THEMES["dark"] if is_dark else THEMES["light"]
toggle_label = "☀️  Light Mode" if is_dark else "🌙  Dark Mode"
mode_badge   = "🌙" if is_dark else "☀️"

# LangSmith status
ls_enabled = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
ls_project  = os.getenv("LANGCHAIN_PROJECT", "sql-talk-bot")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Outfit:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {{
  font-family: 'Outfit', sans-serif !important;
  background-color: {T['bg_app']} !important;
  color: {T['font_primary']} !important;
  transition: background-color 0.3s, color 0.3s;
}}
.stApp {{ background: {T['bg_app']} !important; }}
.main .block-container {{ padding-top: 1.4rem; max-width: 920px; }}

h1 {{ color: {T['font_heading']} !important; font-weight: 700 !important; letter-spacing:-0.6px; margin-bottom:2px !important; }}
h2 {{ color: {T['font_heading']} !important; font-weight: 600 !important; }}
h3 {{ color: {T['font_subheading']} !important; font-weight: 500 !important; font-size:0.95rem !important; }}
p, li {{ color: {T['font_primary']} !important; }}
strong {{ color: {T['font_heading']} !important; }}
em {{ color: {T['font_muted']} !important; }}
code {{
  font-family: 'JetBrains Mono', monospace !important;
  background: {T['bg_sql']} !important;
  color: {T['font_code']} !important;
  padding: 2px 7px; border-radius: 5px; font-size: 0.81em;
  border: 1px solid {T['border_sql']};
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
  background: {T['bg_sidebar']} !important;
  border-right: 1px solid {T['border_divider']};
}}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] li {{ color: {T['font_sidebar']} !important; }}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{ color: {T['font_heading']} !important; }}
section[data-testid="stSidebar"] strong {{ color: {T['font_heading']} !important; }}
section[data-testid="stSidebar"] code {{
  color: {T['font_code']} !important;
  background: {T['bg_sql']} !important;
}}

/* File uploader */
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] p {{ color: {T['font_label']} !important; }}
[data-testid="stFileUploader"] section {{
  background: {T['bg_input']} !important;
  border: 1.5px dashed {T['border_button']} !important;
  border-radius: 12px !important;
  transition: border-color 0.2s;
}}
[data-testid="stFileUploader"] section:hover {{
  border-color: {T['accent_bot']} !important;
}}
[data-testid="stFileUploader"] section * {{ color: {T['font_muted']} !important; }}

/* Buttons */
div[data-testid="stButton"] > button {{
  background: {T['bg_button']} !important;
  border: 1.5px solid {T['border_button']} !important;
  border-radius: 20px !important;
  color: {T['font_button']} !important;
  font-family: 'Outfit', sans-serif !important;
  font-weight: 500 !important;
  font-size: 0.87rem !important;
  padding: 5px 18px !important;
  transition: all 0.2s ease !important;
  letter-spacing: 0.02em !important;
}}
div[data-testid="stButton"] > button:hover {{
  border-color: {T['accent_bot']} !important;
  color: {T['accent_bot']} !important;
  background: {T['bg_bot_msg']} !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px {T['shadow']};
}}

/* Chat input */
[data-testid="stChatInput"] textarea {{
  background: {T['bg_input']} !important;
  color: {T['font_primary']} !important;
  border: 1.5px solid {T['border_button']} !important;
  border-radius: 14px !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 0.95rem !important;
  transition: border-color 0.2s !important;
}}
[data-testid="stChatInput"] textarea:focus {{
  border-color: {T['accent_bot']} !important;
  box-shadow: 0 0 0 3px {T['bg_bot_msg']} !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{ color: {T['font_muted']} !important; }}
[data-testid="stChatInput"] button {{ color: {T['accent_bot']} !important; }}

/* Expander */
details {{
  background: {T['bg_expander']} !important;
  border: 1px solid {T['border_divider']} !important;
  border-radius: 10px !important; padding: 4px 10px;
  margin-top: 6px;
}}
details summary {{
  color: {T['font_muted']} !important; font-size: 0.81rem !important;
  font-family: 'Outfit', sans-serif !important; cursor: pointer;
}}
details p, details span, details div {{
  color: {T['font_primary']} !important; font-size: 0.82rem !important;
}}

/* Alerts */
[data-testid="stAlert"] {{
  background: {T['bg_schema']} !important;
  border-radius: 10px !important;
  border: 1px solid {T['border_card']} !important;
}}
[data-testid="stAlert"] p {{ color: {T['font_primary']} !important; }}

/* Spinner */
[data-testid="stSpinner"] p {{ color: {T['font_thinking']} !important; }}

hr {{ border-color: {T['border_divider']} !important; opacity:0.5; margin: 0.8rem 0 !important; }}

/* ═══════════════════════════════════════════════
   CUSTOM COMPONENTS
═══════════════════════════════════════════════ */

/* Header row */
.header-row {{
  display: flex; align-items: center;
  justify-content: space-between;
  margin-bottom: 2px;
}}
.header-left h1 {{ margin: 0 !important; }}
.header-badges {{
  display: flex; align-items: center; gap: 10px;
}}
.badge-mode {{
  font-size: 0.72rem; font-weight: 600;
  color: {T['font_badge']};
  background: {T['bg_card']};
  border: 1px solid {T['border_card']};
  padding: 3px 10px; border-radius: 20px;
  letter-spacing: 0.05em;
}}
.badge-ls-on {{
  font-size: 0.72rem; font-weight: 600;
  color: {T['font_ls_on']};
  background: {T['bg_stat']};
  border: 1px solid {T['border_info']};
  padding: 3px 10px; border-radius: 20px;
  letter-spacing: 0.04em;
}}
.badge-ls-off {{
  font-size: 0.72rem; font-weight: 600;
  color: {T['font_ls_off']};
  background: {T['bg_card']};
  border: 1px solid {T['border_card']};
  padding: 3px 10px; border-radius: 20px;
  letter-spacing: 0.04em;
}}
.sub-header {{
  color: {T['font_subheading']}; font-size: 0.88rem;
  margin: 2px 0 0 0; padding: 0;
}}

/* Chat messages */
.user-msg {{
  background: {T['bg_user_msg']};
  border-left: 3px solid {T['accent_user']};
  border-radius: 0 12px 12px 12px;
  padding: 14px 18px; margin: 12px 0 6px 0;
  color: {T['font_user_msg']}; font-size: 0.95rem; line-height: 1.65;
  box-shadow: 0 2px 12px {T['shadow']};
  transition: all 0.2s;
}}
.bot-msg {{
  background: {T['bg_bot_msg']};
  border-left: 3px solid {T['accent_bot']};
  border-radius: 0 12px 12px 12px;
  padding: 14px 18px; margin: 6px 0 12px 0;
  color: {T['font_bot_msg']}; font-size: 0.95rem; line-height: 1.65;
  box-shadow: 0 2px 12px {T['shadow']};
  transition: all 0.2s;
}}
.msg-label {{
  font-size: 0.68rem; font-weight: 700;
  letter-spacing: 0.1em; text-transform: uppercase;
  margin-bottom: 6px; display: flex; align-items: center; gap: 6px;
}}
.user-msg .msg-label {{ color: {T['accent_user']}; }}
.bot-msg  .msg-label {{ color: {T['accent_bot']}; }}
.msg-dot {{
  width: 6px; height: 6px; border-radius: 50%; display: inline-block;
}}
.user-msg .msg-dot {{ background: {T['accent_user']}; }}
.bot-msg  .msg-dot {{ background: {T['accent_bot']}; }}

/* SQL block */
.sql-block {{
  background: {T['bg_sql']};
  border: 1px solid {T['border_sql']};
  border-radius: 10px; padding: 12px 16px; margin-top: 10px;
  font-family: 'JetBrains Mono', monospace; font-size: 0.82rem;
  color: {T['font_sql']}; line-height: 1.65;
  position: relative;
}}
.sql-label {{
  font-size: 0.65rem; letter-spacing: 0.12em; text-transform: uppercase;
  color: {T['font_muted']}; margin-bottom: 6px;
  font-family: 'Outfit', sans-serif; font-weight: 600;
  display: flex; align-items: center; gap: 5px;
}}

/* Schema */
.schema-table {{
  background: {T['bg_schema']}; border: 1px solid {T['border_schema']};
  border-radius: 8px; padding: 10px 14px;
  font-family: 'JetBrains Mono', monospace; font-size: 0.79rem;
  color: {T['font_schema']}; line-height: 1.9;
}}

/* File info banner */
.file-banner {{
  background: {T['bg_card']};
  border: 1px solid {T['border_card']};
  border-radius: 14px; padding: 16px 20px; margin-bottom: 16px;
  box-shadow: 0 2px 16px {T['shadow']};
}}
.file-banner-top {{
  display: flex; align-items: center;
  justify-content: space-between; margin-bottom: 14px;
}}
.file-banner-name {{
  font-weight: 600; font-size: 0.95rem;
  color: {T['font_heading']}; letter-spacing: -0.2px;
}}
.file-type-tag {{
  display: inline-block; background: {T['tag_bg']};
  color: {T['tag_color']}; font-size: 0.68rem; font-weight: 700;
  padding: 3px 10px; border-radius: 10px;
  letter-spacing: 0.08em; text-transform: uppercase;
}}
.stat-grid {{
  display: flex; gap: 0; border-radius: 10px; overflow: hidden;
  border: 1px solid {T['border_card']};
}}
.stat-item {{
  flex: 1; text-align: center; padding: 10px 8px;
  background: {T['bg_stat']};
  border-right: 1px solid {T['border_card']};
}}
.stat-item:last-child {{ border-right: none; }}
.stat-val {{
  font-size: 1.3rem; font-weight: 700;
  color: {T['font_stat_val']}; font-family: 'Outfit', sans-serif;
  line-height: 1.2;
}}
.stat-lbl {{
  font-size: 0.65rem; color: {T['font_stat_lbl']};
  text-transform: uppercase; letter-spacing: 0.07em; margin-top: 2px;
}}

/* LangSmith panel */
.ls-panel {{
  background: {T['bg_card']};
  border: 1px solid {T['border_card']};
  border-radius: 12px; padding: 13px 16px;
  margin-top: 8px;
}}
.ls-row {{
  display: flex; align-items: center;
  justify-content: space-between;
}}
.ls-title {{
  font-size: 0.78rem; font-weight: 600;
  color: {T['font_subheading']}; letter-spacing: 0.04em;
}}
.ls-status-on {{
  font-size: 0.72rem; font-weight: 700;
  color: {T['font_ls_on']}; letter-spacing: 0.05em;
}}
.ls-status-off {{
  font-size: 0.72rem; font-weight: 700;
  color: {T['font_ls_off']}; letter-spacing: 0.05em;
}}
.ls-detail {{
  font-size: 0.75rem; color: {T['font_muted']};
  margin-top: 6px; line-height: 1.6;
}}
.ls-detail a {{
  color: {T['font_info']} !important;
  text-decoration: none;
}}
.ls-detail a:hover {{ text-decoration: underline; }}

/* Format tags */
.fmt-row {{
  display: flex; align-items: baseline;
  gap: 8px; margin-bottom: 5px;
}}
.fmt-label {{
  font-size: 0.84rem; font-weight: 500;
  color: {T['font_sidebar']}; min-width: 80px;
}}
.fmt-ext {{
  font-size: 0.75rem; color: {T['font_muted']};
  font-family: 'JetBrains Mono', monospace;
}}

/* Example tips */
.tip-item {{
  padding: 4px 0;
  border-bottom: 1px solid {T['border_divider']};
  margin-bottom: 2px;
}}
.tip-item:last-child {{ border-bottom: none; }}

/* Upload hint */
.upload-hint {{
  text-align: center; padding: 72px 32px;
  color: {T['font_empty']}; font-size: 1rem; line-height: 2.3;
}}
.upload-hint strong {{
  color: {T['font_subheading']} !important; font-size: 1.2rem;
  display: block; margin-bottom: 4px;
}}
.upload-hint .hint-formats {{
  display: flex; justify-content: center; gap: 8px;
  flex-wrap: wrap; margin: 8px 0;
}}
.hint-tag {{
  background: {T['bg_card']};
  border: 1px solid {T['border_card']};
  color: {T['font_label']} !important;
  font-size: 0.78rem; padding: 3px 12px;
  border-radius: 20px; font-family: 'JetBrains Mono', monospace;
}}

/* Thinking indicator */
.thinking-bar {{
  background: {T['bg_thinking']};
  border: 1px solid {T['border_divider']};
  border-radius: 8px; padding: 10px 16px;
  color: {T['font_thinking']}; font-size: 0.84rem;
  display: flex; align-items: center; gap: 10px;
  margin: 8px 0;
}}
/* ═══════════════════════════════════════════
   SQL PANEL
═══════════════════════════════════════════ */
.sql-panel {{
  background: {T['bg_sql']};
  border: 1px solid {T['border_sql']};
  border-radius: 12px;
  margin-top: 10px;
  margin-bottom: 6px;
  overflow: hidden;
  box-shadow: 0 4px 20px {T['shadow']};
  font-family: 'JetBrains Mono', monospace;
}}
.sql-panel-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: {T['bg_card']};
  border-bottom: 1px solid {T['border_sql']};
}}
.sql-panel-title {{
  display: flex;
  align-items: center;
  gap: 7px;
}}
.sql-dot-red    {{ width:11px;height:11px;border-radius:50%;background:#ff5f57;display:inline-block; }}
.sql-dot-yellow {{ width:11px;height:11px;border-radius:50%;background:#febc2e;display:inline-block; }}
.sql-dot-green  {{ width:11px;height:11px;border-radius:50%;background:#28c840;display:inline-block; }}
.sql-panel-label {{
  font-family: 'Outfit', sans-serif;
  font-size: 0.78rem;
  font-weight: 600;
  color: {T['font_subheading']};
  letter-spacing: 0.05em;
  margin-left: 4px;
}}
.sql-panel-badges {{
  display: flex;
  align-items: center;
  gap: 8px;
}}
.sql-badge-lines {{
  font-family: 'Outfit', sans-serif;
  font-size: 0.68rem;
  font-weight: 600;
  color: {T['font_muted']};
  background: {T['bg_schema']};
  border: 1px solid {T['border_schema']};
  padding: 2px 9px;
  border-radius: 10px;
  letter-spacing: 0.05em;
}}
.sql-badge-ok {{
  font-family: 'Outfit', sans-serif;
  font-size: 0.68rem;
  font-weight: 700;
  color: {T['font_ls_on']};
  background: {T['bg_stat']};
  border: 1px solid {T['border_info']};
  padding: 2px 9px;
  border-radius: 10px;
  letter-spacing: 0.05em;
}}
.sql-panel-body {{
  display: flex;
  min-height: 48px;
}}
.sql-line-nums {{
  padding: 14px 12px;
  text-align: right;
  color: {T['font_muted']};
  font-size: 0.78rem;
  line-height: 1.7;
  border-right: 1px solid {T['border_sql']};
  background: {T['bg_card']};
  min-width: 36px;
  user-select: none;
  white-space: pre;
  opacity: 0.6;
}}
.sql-code-area {{
  padding: 14px 18px;
  flex: 1;
  overflow-x: auto;
}}
.sql-panel-footer {{
  padding: 8px 16px;
  border-top: 1px solid {T['border_sql']};
  background: {T['bg_card']};
  display: flex;
  align-items: center;
  justify-content: space-between;
}}

/* ═══════════════════════════════════════════════
   TAB NAVIGATION
═══════════════════════════════════════════════ */
.tab-nav {{
  display: flex; gap: 4px; margin-bottom: 18px;
  background: {T['bg_card']};
  border: 1px solid {T['border_card']};
  border-radius: 12px; padding: 5px;
}}
.tab-btn {{
  flex: 1; text-align: center;
  padding: 9px 16px; border-radius: 8px;
  font-family: 'Outfit', sans-serif;
  font-size: 0.86rem; font-weight: 500;
  cursor: pointer; transition: all 0.2s;
  letter-spacing: 0.02em; border: none;
}}
.tab-active {{
  background: {T['bg_sql']};
  color: {T['accent_bot']} !important;
  border: 1px solid {T['border_sql']} !important;
  font-weight: 600 !important;
}}
.tab-inactive {{
  background: transparent;
  color: {T['font_muted']} !important;
  border: 1px solid transparent !important;
}}

/* ═══════════════════════════════════════════════
   SQL HISTORY LOG
═══════════════════════════════════════════════ */
.sql-log-empty {{
  text-align: center; padding: 56px 24px;
  color: {T['font_empty']}; font-size: 0.92rem; line-height: 2.1;
}}
.sql-log-empty strong {{ color: {T['font_subheading']} !important; display:block; margin-bottom:4px; }}
.sql-log-topbar {{
  display: flex; align-items: center;
  justify-content: space-between; margin-bottom: 16px;
}}
.sql-log-title {{
  font-size: 0.92rem; font-weight: 600;
  color: {T['font_heading']}; letter-spacing: -0.2px;
}}
.sql-log-count {{
  font-size: 0.72rem; font-weight: 700;
  color: {T['font_ls_on']};
  background: {T['bg_stat']}; border: 1px solid {T['border_info']};
  padding: 3px 11px; border-radius: 10px; letter-spacing: 0.04em;
}}
.sql-log-entry {{
  background: {T['bg_card']};
  border: 1px solid {T['border_card']};
  border-radius: 12px; margin-bottom: 14px;
  overflow: hidden;
  box-shadow: 0 2px 12px {T['shadow']};
  transition: border-color 0.2s;
}}
.sql-log-entry:hover {{ border-color: {T['border_sql']}; }}
.sql-log-entry-hdr {{
  display: flex; align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: {T['bg_stat']};
  border-bottom: 1px solid {T['border_card']};
}}
.sql-log-left  {{ display: flex; align-items: center; gap: 10px; }}
.sql-log-right {{ display: flex; align-items: center; gap: 8px; }}
.sql-log-num {{
  font-size: 0.68rem; font-weight: 700;
  color: {T['tag_color']}; background: {T['tag_bg']};
  padding: 2px 9px; border-radius: 8px;
  font-family: 'JetBrains Mono', monospace; letter-spacing: 0.06em;
}}
.sql-log-q {{
  font-size: 0.82rem; color: {T['font_primary']};
  font-style: italic; max-width: 500px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}}
.sql-log-time {{
  font-size: 0.67rem; color: {T['font_muted']};
  font-family: 'JetBrains Mono', monospace;
}}
.sql-log-ok {{
  font-size: 0.67rem; font-weight: 700;
  color: {T['font_ls_on']};
  background: {T['bg_sql']}; border: 1px solid {T['border_info']};
  padding: 2px 8px; border-radius: 8px;
}}
.sql-log-body {{
  display: flex; min-height: 40px;
  border-bottom: 1px solid {T['border_card']};
}}
.sql-log-lnum {{
  padding: 12px 10px; text-align: right;
  color: {T['font_muted']}; font-size: 0.76rem; line-height: 1.7;
  border-right: 1px solid {T['border_card']};
  background: {T['bg_app']}; min-width: 30px;
  user-select: none; white-space: pre; opacity: 0.5;
  font-family: 'JetBrains Mono', monospace;
}}
.sql-log-code {{ padding: 12px 16px; flex: 1; overflow-x: auto; }}
.sql-log-foot {{
  padding: 7px 16px;
  font-size: 0.70rem; color: {T['font_muted']};
  display: flex; align-items: center; justify-content: space-between;
}}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in {
    "agent": None, "db": None, "messages": [],
    "db_name": None, "schema_info": None,
    "temp_db_path": None, "file_stats": None,
    "file_type_label": None,
    "sql_history": [],        # ← stores all generated SQL queries
    "active_tab": "chat",    # ← "chat" or "sql_log"
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_schema_display(db) -> dict:
    schema = {}
    try:
        for table in db.get_table_names():
            info = db.get_table_info([table])
            cols = []
            for line in info.splitlines():
                line = line.strip()
                if line and not line.upper().startswith(("CREATE", ")", "/*", "--")):
                    col = line.split()[0].strip('",')
                    if col:
                        cols.append(col)
            schema[table] = cols
    except Exception:
        pass
    return schema

def cleanup_temp():
    if st.session_state.temp_db_path and os.path.exists(st.session_state.temp_db_path):
        try:
            os.remove(st.session_state.temp_db_path)
        except Exception:
            pass

def fmt_number(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


SQL_KEYWORDS = [
    "SELECT","FROM","WHERE","JOIN","LEFT","RIGHT","INNER","OUTER",
    "ON","GROUP","BY","ORDER","HAVING","LIMIT","OFFSET","INSERT",
    "INTO","VALUES","UPDATE","SET","DELETE","CREATE","TABLE",
    "DROP","ALTER","AND","OR","NOT","IN","IS","NULL","AS",
    "DISTINCT","COUNT","SUM","AVG","MIN","MAX","CASE","WHEN",
    "THEN","ELSE","END","UNION","ALL","EXISTS","BETWEEN","LIKE",
]


def highlight_sql(sql_code: str) -> str:
    """Apply keyword highlighting to SQL string."""
    kw_color = T["accent_user"]
    result = sql_code
    for kw in SQL_KEYWORDS:
        result = result.replace(
            f" {kw} ",
            f" <span style='color:{kw_color};font-weight:600'>{kw}</span> "
        ).replace(
            f"\n{kw} ",
            f"\n<span style='color:{kw_color};font-weight:600'>{kw}</span> "
        ).replace(
            f"\n{kw}\n",
            f"\n<span style='color:{kw_color};font-weight:600'>{kw}</span>\n"
        )
    # Handle keyword at very start
    for kw in SQL_KEYWORDS:
        if result.startswith(kw + " ") or result.startswith(kw + "\n"):
            result = (
                f"<span style='color:{kw_color};font-weight:600'>{kw}</span>"
                + result[len(kw):]
            )
            break
    return result


def render_sql_panel(sql: str, db_name: str, panel_id: str = ""):
    """Render the macOS-style SQL panel with line numbers, highlighting, badges."""
    lines     = sql.strip().splitlines()
    line_nums = "\n".join(str(i + 1) for i in range(len(lines)))
    highlighted = highlight_sql("\n".join(lines))
    n         = len(lines)
    fs        = T["font_sql"]
    fm        = T["font_muted"]
    fl        = T["font_label"]

    st.markdown(f"""
    <div class='sql-panel'>
      <div class='sql-panel-header'>
        <div class='sql-panel-title'>
          <span class='sql-dot-red'></span>
          <span class='sql-dot-yellow'></span>
          <span class='sql-dot-green'></span>
          <span class='sql-panel-label'>Generated SQL Query</span>
        </div>
        <div class='sql-panel-badges'>
          <span class='sql-badge-lines'>{n} line{"s" if n != 1 else ""}</span>
          <span class='sql-badge-ok'>✓ Executed</span>
        </div>
      </div>
      <div class='sql-panel-body'>
        <div class='sql-line-nums'>{line_nums}</div>
        <div class='sql-code-area'>
          <pre style='margin:0;font-family:"JetBrains Mono",monospace;font-size:0.85rem;
               line-height:1.7;color:{fs};white-space:pre-wrap;word-break:break-word'>{highlighted}</pre>
        </div>
      </div>
      <div class='sql-panel-footer'>
        <span style='color:{fm};font-size:0.71rem'>
          🔗 Executed against: <strong style='color:{fl}'>{db_name}</strong>
        </span>
        <span style='color:{fm};font-size:0.69rem;font-family:"JetBrains Mono",monospace'>SQLite</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🗄️ SQL Talk Bot")
    st.markdown("Talk to any data file in plain English.")
    st.markdown("---")

    # Theme toggle
    if st.button(toggle_label, key="theme_toggle", use_container_width=True):
        st.session_state.theme = "light" if is_dark else "dark"
        st.rerun()

    st.markdown("---")

    # ── LangSmith panel ───────────────────────────────────────────────────────
    if ls_enabled:
        ls_html = f"""
        <div class='ls-panel'>
          <div class='ls-row'>
            <span class='ls-title'>🔭 LangSmith Tracing</span>
            <span class='ls-status-on'>● ACTIVE</span>
          </div>
          <div class='ls-detail'>
            Project: <strong>{ls_project}</strong><br>
            <a href='https://smith.langchain.com' target='_blank'>
              Open Dashboard ↗
            </a>
          </div>
        </div>
        """
    else:
        ls_html = f"""
        <div class='ls-panel'>
          <div class='ls-row'>
            <span class='ls-title'>🔭 LangSmith Tracing</span>
            <span class='ls-status-off'>○ OFF</span>
          </div>
          <div class='ls-detail'>
            Add <code>LANGCHAIN_TRACING_V2=true</code><br>
            and <code>LANGCHAIN_API_KEY</code> to <code>.env</code>
          </div>
        </div>
        """
    st.markdown(ls_html, unsafe_allow_html=True)
    st.markdown("---")

    # ── Supported formats ─────────────────────────────────────────────────────
    st.markdown("### 📁 Supported Formats")
    muted = T["font_muted"]
    formats = [
        ("🗄️ SQLite",  ".db · .sqlite · .sqlite3"),
        ("📊 Excel",   ".xlsx · .xls · .xlsm"),
        ("📄 CSV",     ".csv"),
        ("📋 JSON",    ".json"),
        ("⚡ Parquet", ".parquet"),
    ]
    for label, exts in formats:
        ext_color = T["font_muted"]
        st.markdown(
            f"<div class='fmt-row'>"
            f"<span class='fmt-label'>{label}</span>"
            f"<span class='fmt-ext' style='color:{ext_color}'>{exts}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── File uploader ─────────────────────────────────────────────────────────
    uploaded_file = st.file_uploader(
        "Upload your data file",
        type=list(SUPPORTED_TYPES.keys()),
        help="SQLite, Excel, CSV, JSON, or Parquet",
    )

    if uploaded_file:
        if uploaded_file.name != st.session_state.db_name:
            cleanup_temp()
            st.session_state.messages  = []
            st.session_state.sql_history = []
            with st.spinner("🔄 Converting & loading…"):
                try:
                    if not is_supported(uploaded_file.name):
                        st.error("❌ Unsupported file type.")
                    else:
                        db_path, tables, counts = convert_to_sqlite(uploaded_file)
                        agent, db = build_agent(db_path)
                        total_rows = sum(counts.values())
                        schema     = get_schema_display(db)
                        total_cols = sum(len(c) for c in schema.values())

                        st.session_state.agent           = agent
                        st.session_state.db              = db
                        st.session_state.db_name         = uploaded_file.name
                        st.session_state.temp_db_path    = db_path
                        st.session_state.schema_info     = schema
                        st.session_state.file_type_label = get_file_label(uploaded_file.name)
                        st.session_state.file_stats      = {
                            "tables": len(tables),
                            "rows":   total_rows,
                            "cols":   total_cols,
                        }
                        st.success(f"✅ Ready: **{uploaded_file.name}**")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    st.session_state.agent = None

    # ── Schema viewer ─────────────────────────────────────────────────────────
    if st.session_state.schema_info:
        st.markdown("---")
        st.markdown("### 📊 Schema")
        for table, cols in st.session_state.schema_info.items():
            with st.expander(f"📋 {table}", expanded=False):
                st.markdown(
                    "<div class='schema-table'>"
                    + "<br>".join(f"• {c}" for c in cols)
                    + "</div>",
                    unsafe_allow_html=True,
                )

    if st.session_state.agent:
        st.markdown("---")
        if st.button("🗑️  Clear Chat", key="clear_chat", use_container_width=True):
            st.session_state.messages   = []
            st.session_state.sql_history = []
            st.rerun()
        st.markdown("---")
        st.markdown("### 💡 Try asking")
        tips = [
            "Show me all tables",
            "How many rows in each table?",
            "First 5 rows of [table]",
            "Total sales by category",
            "Top 10 by [column]",
            "Find duplicates in [column]",
            "Average [col] grouped by [col]",
            "Rows where [col] > 1000",
        ]
        tip_color = T["font_tip"]
        code_color = T["font_code"]
        bg_sql = T["bg_sql"]
        for tip in tips:
            st.markdown(
                f"<div class='tip-item'>"
                f"<span style='color:{tip_color}'>› </span>"
                f"<code style='color:{code_color};background:{bg_sql}'>{tip}</code>"
                f"</div>",
                unsafe_allow_html=True,
            )


# ── Header ────────────────────────────────────────────────────────────────────
ls_badge = (
    f"<span class='badge-ls-on'>● LangSmith: {ls_project}</span>"
    if ls_enabled else
    f"<span class='badge-ls-off'>○ LangSmith off</span>"
)
st.markdown(f"""
<div class='header-row'>
  <div class='header-left'>
    <h1>🗄️ SQL Talk Bot</h1>
  </div>
  <div class='header-badges'>
    {ls_badge}
    <span class='badge-mode'>{mode_badge} {'Dark' if is_dark else 'Light'}</span>
  </div>
</div>
<p class='sub-header'>
  Powered by <strong>Llama-3.3</strong> ·
  <strong>LangChain</strong> ·
  <strong>Groq</strong> ·
  <strong>LangSmith</strong>
</p>
""", unsafe_allow_html=True)
st.divider()


# ── No file state ─────────────────────────────────────────────────────────────
if not st.session_state.agent:
    st.markdown("""
    <div class='upload-hint'>
      <strong>📂 No data file loaded</strong>
      Upload your file from the sidebar to get started.<br>
      <div class='hint-formats'>
        <span class='hint-tag'>.db</span>
        <span class='hint-tag'>.xlsx</span>
        <span class='hint-tag'>.csv</span>
        <span class='hint-tag'>.json</span>
        <span class='hint-tag'>.parquet</span>
      </div>
      <em>All processing is local — your data never leaves your machine.</em>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── File info banner ──────────────────────────────────────────────────────────
if st.session_state.file_stats:
    s  = st.session_state.file_stats
    ft = st.session_state.file_type_label or ""
    fn = st.session_state.db_name or ""
    st.markdown(f"""
    <div class='file-banner'>
      <div class='file-banner-top'>
        <span class='file-banner-name'>📁 {fn}</span>
        <span class='file-type-tag'>{ft}</span>
      </div>
      <div class='stat-grid'>
        <div class='stat-item'>
          <div class='stat-val'>{s['tables']}</div>
          <div class='stat-lbl'>Tables</div>
        </div>
        <div class='stat-item'>
          <div class='stat-val'>{fmt_number(s['rows'])}</div>
          <div class='stat-lbl'>Rows</div>
        </div>
        <div class='stat-item'>
          <div class='stat-val'>{s['cols']}</div>
          <div class='stat-lbl'>Columns</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── Tab Navigation ────────────────────────────────────────────────────────────
sql_count   = len(st.session_state.sql_history)
chat_active = st.session_state.active_tab == "chat"
log_active  = st.session_state.active_tab == "sql_log"

chat_cls = "tab-btn tab-active" if chat_active else "tab-btn tab-inactive"
log_cls  = "tab-btn tab-active" if log_active  else "tab-btn tab-inactive"
log_pill = f" ({sql_count})" if sql_count > 0 else ""

col_chat, col_log = st.columns(2)
with col_chat:
    if st.button(
        f"💬  Chat",
        key="tab_chat",
        use_container_width=True,
        type="primary" if chat_active else "secondary",
    ):
        st.session_state.active_tab = "chat"
        st.rerun()
with col_log:
    if st.button(
        f"🗃️  SQL Query Log{log_pill}",
        key="tab_log",
        use_container_width=True,
        type="primary" if log_active else "secondary",
    ):
        st.session_state.active_tab = "sql_log"
        st.rerun()

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# TAB A — CHAT
# ════════════════════════════════════════════════════════
if st.session_state.active_tab == "chat":

    # Chat history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f"<div class='user-msg'>"
                f"<div class='msg-label'><span class='msg-dot'></span>You</div>"
                f"{msg['content']}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div class='bot-msg'>"
                f"<div class='msg-label'><span class='msg-dot'></span>Assistant</div>"
                f"{msg['content']}</div>",
                unsafe_allow_html=True,
            )
            if msg.get("sql"):
                render_sql_panel(msg["sql"], st.session_state.db_name or "")
            if msg.get("steps"):
                with st.expander("🔎 Agent reasoning steps"):
                    for i, step in enumerate(msg["steps"], 1):
                        st.markdown(f"**Step {i}:** `{step}`")

    # Chat input
    user_input = st.chat_input(f"Ask something about {st.session_state.db_name}…")

    if user_input:
        import datetime
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.markdown(
            f"<div class='user-msg'>"
            f"<div class='msg-label'><span class='msg-dot'></span>You</div>"
            f"{user_input}</div>",
            unsafe_allow_html=True,
        )

        with st.spinner("🧠 Querying your data…"):
            result = query_agent(st.session_state.agent, user_input)

        if result["error"]:
            answer, sql_used = f"⚠️ {result['error']}", None
        else:
            answer   = result["answer"]
            sql_used = None
            for step in result["steps"]:
                if isinstance(step, tuple) and len(step) == 2:
                    action, _ = step
                    if hasattr(action, "tool") and "sql" in action.tool.lower():
                        sql_used = getattr(action, "tool_input", {}).get("query")

        # Save to sql_history if we got a query
        if sql_used:
            st.session_state.sql_history.append({
                "n":        len(st.session_state.sql_history) + 1,
                "question": user_input,
                "sql":      sql_used,
                "time":     datetime.datetime.now().strftime("%H:%M:%S"),
                "db":       st.session_state.db_name or "",
            })

        st.session_state.messages.append({
            "role": "assistant", "content": answer,
            "sql": sql_used,
            "steps": [str(s) for s in result["steps"]],
        })

        st.markdown(
            f"<div class='bot-msg'>"
            f"<div class='msg-label'><span class='msg-dot'></span>Assistant</div>"
            f"{answer}</div>",
            unsafe_allow_html=True,
        )
        if sql_used:
            render_sql_panel(sql_used, st.session_state.db_name or "")

        st.rerun()

# ════════════════════════════════════════════════════════
# TAB B — SQL QUERY LOG
# ════════════════════════════════════════════════════════
else:
    history = st.session_state.sql_history

    if not history:
        st.markdown("""
        <div class='sql-log-empty'>
          <strong>🗃️ No SQL queries yet</strong>
          Switch to Chat and ask a question —<br>
          every generated SQL query will appear here.
        </div>
        """, unsafe_allow_html=True)

    else:
        # Top bar: title + count + clear button
        hcol1, hcol2 = st.columns([4, 1])
        with hcol1:
            count_color = T["font_ls_on"]
            bg_stat     = T["bg_stat"]
            border_info = T["border_info"]
            fh          = T["font_heading"]
            st.markdown(
                f"<div class='sql-log-topbar'>"
                f"<span class='sql-log-title'>🗃️ SQL Query Log</span>"
                f"<span class='sql-log-count' style='color:{count_color};"
                f"background:{bg_stat};border:1px solid {border_info}'>"
                f"{len(history)} quer{'y' if len(history)==1 else 'ies'}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with hcol2:
            if st.button("🗑️ Clear Log", key="clear_sql_log", use_container_width=True):
                st.session_state.sql_history = []
                st.rerun()

        # Render entries newest-first
        for entry in reversed(history):
            lines     = entry["sql"].strip().splitlines()
            line_nums = "\n".join(str(i + 1) for i in range(len(lines)))
            highlighted = highlight_sql("\n".join(lines))
            n_lines   = len(lines)
            fs        = T["font_sql"]
            fm        = T["font_muted"]
            fl        = T["font_label"]
            fp        = T["font_primary"]
            fa        = T["bg_app"]
            bc        = T["border_card"]

            st.markdown(f"""
            <div class='sql-log-entry'>
              <div class='sql-log-entry-hdr'>
                <div class='sql-log-left'>
                  <span class='sql-log-num'>#{entry['n']:02d}</span>
                  <span class='sql-log-q' style='color:{fp}'>{entry['question']}</span>
                </div>
                <div class='sql-log-right'>
                  <span class='sql-log-time'>{entry['time']}</span>
                  <span class='sql-log-ok'>✓ Executed</span>
                </div>
              </div>
              <div class='sql-log-body'>
                <div class='sql-log-lnum' style='background:{fa};border-right:1px solid {bc}'>{line_nums}</div>
                <div class='sql-log-code'>
                  <pre style='margin:0;font-family:"JetBrains Mono",monospace;font-size:0.84rem;
                       line-height:1.7;color:{fs};white-space:pre-wrap;word-break:break-word'>{highlighted}</pre>
                </div>
              </div>
              <div class='sql-log-foot'>
                <span style='color:{fm}'>🔗 <strong style='color:{fl}'>{entry['db']}</strong></span>
                <span style='color:{fm};font-family:"JetBrains Mono",monospace'>{n_lines} line{"s" if n_lines!=1 else ""}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)