from winreg import OpenKey, HKEY_CURRENT_USER, KEY_READ, EnumValue

def get_theme() -> str:
    try:
        if EnumValue(OpenKey(HKEY_CURRENT_USER, r'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize\\', 0, KEY_READ), 2)[1]:
            return 'Light'
        return 'Dark'
    except Exception:
        return 'Dark'
