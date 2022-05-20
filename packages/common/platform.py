class win:
    def disable_console_quick_edit_mode():
        from .win_types import (update_console_mode, ENABLE_EXTENDED_FLAGS, ENABLE_QUICK_EDIT_MODE)
        mask = ENABLE_EXTENDED_FLAGS | ENABLE_QUICK_EDIT_MODE
        flags = ENABLE_EXTENDED_FLAGS
        update_console_mode(flags, mask, restore=True)