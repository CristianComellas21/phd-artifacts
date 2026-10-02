from questionary import Style
from rich.theme import Theme

RICH_THEME = Theme(
    {
        "success": "green",
        "error": "red",
        "warning": "yellow",
        "info": "cyan",
        "accent": "bold cyan",
        "muted": "dim",
    }
)


QUESTIONARY_STYLE = Style(
    [
        ("qmark", "fg:#00d7af bold"),
        ("question", "bold"),
        ("answer", "fg:#00d7af bold"),
        ("pointer", "fg:#00d7af bold"),
        ("highlighted", "fg:#00d7af bold"),
        ("selected", "fg:#00d7af"),
        ("separator", "fg:#6c6c6c"),
        ("instruction", "fg:#808080"),
        ("text", ""),
        ("disabled", "fg:#858585 italic"),
    ]
)


QUESTIONARY_DEFAULTS = {
    "style": QUESTIONARY_STYLE,
    "qmark": "❓",
    "pointer": "❯",
}
