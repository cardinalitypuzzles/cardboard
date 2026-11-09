from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def vite_asset(entry_path="hunts/src/index.tsx"):
    """
    Renders React script tags.
    In development (when DEBUG is True or VITE_DEV_MODE is True),
    injects Vite's React Fast Refresh preamble, HMR client, and ES module entry.
    In production, falls back to the compiled static bundle (main.js).
    """
    dev_mode = getattr(settings, "VITE_DEV_MODE", settings.DEBUG)
    vite_server_url = getattr(
        settings, "VITE_SERVER_URL", "http://localhost:5173"
    ).rstrip("/")

    if dev_mode:
        return mark_safe(
            f"""<script type="module">
    import RefreshRuntime from '{vite_server_url}/@react-refresh';
    RefreshRuntime.injectIntoGlobalHook(window);
    window.$RefreshReg$ = () => {{}};
    window.$RefreshSig$ = () => (type) => type;
    window.__vite_plugin_react_preamble_installed__ = true;
</script>
<script type="module" src="{vite_server_url}/@vite/client"></script>
<script type="module" src="{vite_server_url}/{entry_path}"></script>"""
        )

    bundle_url = static("main.js")
    return mark_safe(f'<script src="{bundle_url}"></script>')
