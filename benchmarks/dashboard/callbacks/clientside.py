from dash import Input, Output, State

from benchmarks.dashboard.dash_mixin import dashed


@dashed(
    Output("dummy_theme", "data"),
    Input("theme", "data"),
    State("n_changes_theme", "data"),
)
def client_main():
    """
    function(theme, n_clicks) {
        var stylesheet = document.querySelector('link[rel=stylesheet][href^="https://stackpath"], link[rel=stylesheet][href^="https://cdn"]') // # noqa: E501

        var name = JSON.parse(theme);
        var changes = JSON.parse(n_clicks);

        let darkMode = document.querySelector('.dark-mode');
        let themeSwitch = document.getElementById('theme-switch');

        if (name === 'dark') {
            var link = "https://cdn.jsdelivr.net/npm/bootswatch@5.1.3/dist/cyborg/bootstrap.min.css"
          } else {
            var link = "https://cdn.jsdelivr.net/npm/bootswatch@5.1.3/dist/litera/bootstrap.min.css"
        }

        if (changes > 2) {
            darkMode.classList.toggle('active');
        }

        function changeTheme() {
            stylesheet.href = link
        }

        setTimeout(changeTheme, 500);
    }
    """
