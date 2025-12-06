"""Reusable UI components for Maya tools built with PySide6.

This module defines small widgets and a base dialog class suitable for creating
Maya-dockable tools. All dialogs inherit MayaQWidgetDockableMixin to support
workspace control docking inside Maya.
"""

from PySide6 import QtWidgets, QtCore
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


class CustomLabel(QtWidgets.QLabel):
    """Colored, center-aligned label used as an axis tag or badge."""

    def __init__(self, parent=None, color="#FFFFFF"):
        """Initialize the label.

        Args:
            parent (QWidget | None): Parent widget.
            color (str): CSS color string used as the background.
        """
        super().__init__(parent)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.set_color(color)
        self.setMinimumWidth(25)

    def set_color(self, color):
        """Apply a background color and common style to the label.

        Args:
            color (str): CSS color string.
        """
        self.setStyleSheet("QLabel { background-color: %s; "
                           "color: #000000; "
                           "border-radius: 2px; "
                           "font-weight: bold;}"
                           % color)


class CustomSpinBox(QtWidgets.QDoubleSpinBox):
    """Spin box preconfigured for angle increments (degrees)."""

    MIN_WIDTH = 40
    DEFAULT_VALUE = 90
    STEP_VALUE = 15
    MINIMUM_VALUE, MAXIMUM_VALUE = -360, 360

    def __init__(self, parent=None):
        """Initialize the spin box with sensible defaults for rotations."""
        super().__init__(parent)
        self.setToolTip("Rotation increment in degrees")
        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.setValue(self.DEFAULT_VALUE)
        self.setDecimals(1)
        self.setRange(self.MINIMUM_VALUE, self.MAXIMUM_VALUE)
        self.setSingleStep(self.STEP_VALUE)
        self.setMinimumWidth(self.MIN_WIDTH)

        # Intercept clicks occurring on the embedded line edit as well
        if self.lineEdit():
            self.lineEdit().installEventFilter(self)

    def mousePressEvent(self, event):
        # Middle-click on the spin box area resets to default
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self.setValue(self.DEFAULT_VALUE)
            event.accept()
            return
        super().mousePressEvent(event)

    def eventFilter(self, obj, event):
        # Middle-click on the inner line edit should behave the same
        # noinspection PyUnresolvedReferences
        if (event.type() == QtCore.QEvent.Type.MouseButtonPress and
                getattr(event, "button", None) and
                event.button() == QtCore.Qt.MouseButton.MiddleButton):
            self.setValue(self.DEFAULT_VALUE)
            return True  # consume the event
        return super().eventFilter(obj, event)


class CustomPushButton(QtWidgets.QPushButton):
    """Push button with consistent height for layout alignment."""

    BUTTON_HEIGHT = 40

    def __init__(self, parent=None):
        """Initialize the button and apply the fixed height."""
        super().__init__(parent)
        self.setFixedHeight(self.BUTTON_HEIGHT)


class CustomDialog(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    """Base dialog that supports Maya workspace docking and a standard setup flow."""

    OBJECT_NAME = "CustomDialog"

    dlg_instance = None

    @classmethod
    def show_dialog(cls):
        """Show a single instance of this dialog docked in Maya.

        If the dialog exists but is hidden, it will be shown; otherwise it is
        raised and activated.
        """
        if not cls.dlg_instance:
            cls.dlg_instance = cls()

        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show(dockable=True)
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self, parent=None):
        """Construct the dialog.

        Subclasses should implement create_widgets, create_layout, and
        create_connections, then call setup_ui() or rely on base init that
        calls it in their own __init__ if desired.
        """
        super().__init__(parent)

    def create_widgets(self):
        """Create child widgets. To be implemented by subclasses."""
        pass

    def create_layout(self):
        """Assemble layouts. To be implemented by subclasses."""
        pass

    def create_connections(self):
        """Connect signals and slots. To be implemented by subclasses."""
        pass


    def setup_ui(self):
        """Set up the UI elements and call subclass hooks in order."""
        self.setWindowTitle(self.OBJECT_NAME)
        self.create_widgets()
        self.create_layout()
        self.create_connections()


    def keyPressEvent(self, e):
        """Override for keyboard shortcuts in derived tools (optional)."""
        pass
