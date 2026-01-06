# AuthCheck - part of the Ningu Framework
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from PySide6.QtWidgets import (
    QWidget, QPlainTextEdit, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QComboBox, QPushButton, QFrame, QGridLayout, 
    QSpacerItem, QSizePolicy, QListWidget, QListWidgetItem,
    QCheckBox, QFormLayout, QScrollArea, QFileDialog
)
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtCore import Qt
import importlib.util
import os
import sys

# Define the version number at the top
VERSION = "1.0.0"

# Define the tab label for the tab widget
TAB_LABEL = f"AuthCheck v{VERSION}"


class Ui_TabContent:
    def setupUi(self, widget):
        """Set up the UI components for the AuthCheck tab."""
        widget.setObjectName("TabContent")

        # Main vertical layout
        self.verticalLayout_main = QVBoxLayout(widget)
        self.verticalLayout_main.setObjectName("verticalLayout_main")
        self.verticalLayout_main.setSpacing(5)

        # Main content frame (list on left, form on right)
        self.frame_content = QFrame(widget)
        self.gridLayout = QGridLayout(self.frame_content)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        # Left side: Module list
        self.frame_list = QFrame(self.frame_content)
        self.frame_list.setFrameShape(QFrame.NoFrame)
        self.verticalLayout_list = QVBoxLayout(self.frame_list)
        self.verticalLayout_list.setContentsMargins(5, 5, 5, 5)

        # Header row: Label + Filter field + Clear button
        self.frame_filter = QFrame(self.frame_list)
        self.frame_filter.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout_filter = QHBoxLayout(self.frame_filter)
        self.horizontalLayout_filter.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_filter.setSpacing(5)

        self.label_modules = QLabel(self.frame_filter)
        self.label_modules.setText("Authentication Systems:")
        label_modules_font = QFont()
        label_modules_font.setBold(True)
        self.label_modules.setFont(label_modules_font)
        self.horizontalLayout_filter.addWidget(self.label_modules)

        self.FilterEdit = QLineEdit(self.frame_filter)
        self.FilterEdit.setPlaceholderText("Filter...")
        self.FilterEdit.setClearButtonEnabled(False)  # We'll use our own clear button
        self.horizontalLayout_filter.addWidget(self.FilterEdit)

        self.FilterClearButton = QPushButton(self.frame_filter)
        self.FilterClearButton.setText("Clear")
        self.FilterClearButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.horizontalLayout_filter.addWidget(self.FilterClearButton)

        self.verticalLayout_list.addWidget(self.frame_filter)

        self.ModulesList = QListWidget(self.frame_list)
        self.verticalLayout_list.addWidget(self.ModulesList)

        self.gridLayout.addWidget(self.frame_list, 0, 0, 1, 1)

        # Right side: Dynamic form area
        self.frame_form = QFrame(self.frame_content)
        self.frame_form.setFrameShape(QFrame.NoFrame)
        self.verticalLayout_form = QVBoxLayout(self.frame_form)
        self.verticalLayout_form.setContentsMargins(5, 5, 5, 5)

        self.label_form_title = QLabel(self.frame_form)
        self.label_form_title.setText("Select an authentication system from the list")
        form_title_font = QFont()
        form_title_font.setBold(True)
        self.label_form_title.setFont(form_title_font)
        self.verticalLayout_form.addWidget(self.label_form_title)

        # Scroll area for the form
        self.scrollArea = QScrollArea(self.frame_form)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        
        self.scrollAreaWidget = QWidget()
        self.formLayout = QFormLayout(self.scrollAreaWidget)
        self.formLayout.setContentsMargins(10, 10, 10, 10)
        self.formLayout.setSpacing(10)
        
        self.scrollArea.setWidget(self.scrollAreaWidget)
        self.verticalLayout_form.addWidget(self.scrollArea)

        # Button frame at bottom of form
        self.frame_buttons = QFrame(self.frame_form)
        self.frame_buttons.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout_buttons = QHBoxLayout(self.frame_buttons)
        self.horizontalLayout_buttons.setContentsMargins(0, 10, 0, 0)

        self.ClearButton = QPushButton(self.frame_buttons)
        self.ClearButton.setText("Clear")
        self.ClearButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.horizontalLayout_buttons.addWidget(self.ClearButton)

        self.horizontalSpacer_buttons = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_buttons.addItem(self.horizontalSpacer_buttons)

        self.CheckButton = QPushButton(self.frame_buttons)
        self.CheckButton.setText("Check")
        font_bold = QFont()
        font_bold.setBold(True)
        self.CheckButton.setFont(font_bold)
        self.CheckButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.horizontalLayout_buttons.addWidget(self.CheckButton)

        self.verticalLayout_form.addWidget(self.frame_buttons)

        self.gridLayout.addWidget(self.frame_form, 0, 1, 1, 1)

        # Set column stretch (list smaller, form larger)
        self.gridLayout.setColumnStretch(0, 2)
        self.gridLayout.setColumnStretch(1, 5)

        self.verticalLayout_main.addWidget(self.frame_content, stretch=1)

        # Bottom: Status window
        self.frame_status = QFrame(widget)
        self.frame_status.setFrameShape(QFrame.NoFrame)
        self.verticalLayout_status = QVBoxLayout(self.frame_status)
        self.verticalLayout_status.setContentsMargins(5, 0, 5, 0)

        self.StatusTextBox = QPlainTextEdit(self.frame_status)
        self.StatusTextBox.setReadOnly(True)
        # Set fixed-width font for StatusTextBox
        status_font = QFont("Courier New", 12)
        status_font.setFixedPitch(True)
        self.StatusTextBox.setFont(status_font)
        self.verticalLayout_status.addWidget(self.StatusTextBox)

        self.verticalLayout_main.addWidget(self.frame_status, stretch=1)


class TabContent(QWidget):
    def __init__(self):
        """Initialize the TabContent widget."""
        super().__init__()
        self.ui = Ui_TabContent()
        self.ui.setupUi(self)

        # Track loaded modules and form widgets
        self.modules = {}
        self.current_module = None
        self.form_widgets = {}  # {module_name: {field_name: widget}}
        self.form_values = {}   # {module_name: {field_name: value}} - persisted values
        self.port_toggle_map = {}  # {module_name: {port_field: {checkbox_field, tls_port, non_tls_port}}}

        # Add module_libs to sys.path
        module_libs_path = os.path.join('modules', 'AuthCheck_module_libs')
        if module_libs_path not in sys.path:
            sys.path.insert(0, module_libs_path)

        # Load authentication modules
        self.load_auth_modules()

        # Connect signals
        self.ui.ModulesList.itemClicked.connect(self.on_module_selected)
        self.ui.ModulesList.currentItemChanged.connect(self.on_module_selected)
        self.ui.ClearButton.clicked.connect(self.clear_form)
        self.ui.CheckButton.clicked.connect(self.check_authentication)
        
        # Filter signals
        self.ui.FilterEdit.textChanged.connect(self.filter_modules)
        self.ui.FilterClearButton.clicked.connect(self.clear_filter)

        # Initially disable buttons until a module is selected
        self.ui.ClearButton.setEnabled(False)
        self.ui.CheckButton.setEnabled(False)

    def load_auth_modules(self):
        """Load all authentication modules from the AuthCheck_modules directory."""
        modules_dir = os.path.join('modules', 'AuthCheck_modules')
        
        # Create directory if it doesn't exist
        os.makedirs(modules_dir, exist_ok=True)
        
        # Temporary list to hold module info for sorting
        module_list = []
        
        if os.path.isdir(modules_dir):
            for filename in os.listdir(modules_dir):
                if filename.endswith('.py') and filename != '__init__.py':
                    module_name = filename[:-3]
                    file_path = os.path.join(modules_dir, filename)
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if spec is None:
                        self.ui.StatusTextBox.appendPlainText(f"Error: Could not create spec for {filename}")
                        continue
                    module = importlib.util.module_from_spec(spec)
                    try:
                        spec.loader.exec_module(module)
                        # Verify module has required attributes
                        if hasattr(module, 'form_fields') and hasattr(module, 'authenticate'):
                            self.modules[module_name] = module
                            display_name = getattr(module, 'module_description', module_name)
                            module_list.append((display_name, module_name))
                            # Initialize form values storage
                            self.form_values[module_name] = {}
                        else:
                            self.ui.StatusTextBox.appendPlainText(
                                f"Warning: {filename} missing 'form_fields' or 'authenticate'"
                            )
                    except Exception as e:
                        self.ui.StatusTextBox.appendPlainText(f"Error loading {filename}: {e}")
        
        # Sort by display name (case-insensitive) and add to list widget
        for display_name, module_name in sorted(module_list, key=lambda x: x[0].lower()):
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, module_name)
            self.ui.ModulesList.addItem(item)
        
        if not self.modules:
            self.ui.StatusTextBox.appendPlainText("No authentication modules found in 'modules/AuthCheck_modules/'")
        else:
            self.ui.StatusTextBox.appendPlainText(f"Loaded {len(self.modules)} authentication modules.")

    def filter_modules(self, filter_text):
        """Filter the modules list based on the filter text."""
        filter_text = filter_text.lower()
        
        for i in range(self.ui.ModulesList.count()):
            item = self.ui.ModulesList.item(i)
            display_name = item.text().lower()
            module_name = item.data(Qt.UserRole).lower()
            
            # Show item if filter text is found in display name or module name
            if filter_text in display_name or filter_text in module_name:
                item.setHidden(False)
            else:
                item.setHidden(True)

    def clear_filter(self):
        """Clear the filter text and show all modules."""
        self.ui.FilterEdit.clear()

    def on_module_selected(self, item, previous=None):
        """Handle module selection from the list."""
        if item is None:
            return
        module_name = item.data(Qt.UserRole)
        if module_name == self.current_module:
            return  # Already selected
        
        # Save current form values before switching
        if self.current_module:
            self.save_form_values()
        
        self.current_module = module_name
        module = self.modules[module_name]
        
        # Update form title
        display_name = getattr(module, 'module_description', module_name)
        self.ui.label_form_title.setText(display_name)
        
        # Build the form
        self.build_form(module_name, module)
        
        # Enable buttons
        self.ui.ClearButton.setEnabled(True)
        self.ui.CheckButton.setEnabled(True)

    def build_form(self, module_name, module):
        """Build the dynamic form based on module's form_fields."""
        # Clear existing form widgets
        while self.ui.formLayout.count():
            item = self.ui.formLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.form_widgets[module_name] = {}
        self.port_toggle_map[module_name] = {}
        form_fields = getattr(module, 'form_fields', [])
        
        # Get saved values for this module
        saved_values = self.form_values.get(module_name, {})
        
        # First pass: identify port toggle relationships
        port_toggles = {}  # {port_field_name: {checkbox, tls_port, non_tls_port}}
        for field in form_fields:
            if field.get('port_toggle'):
                port_field_name = field.get('name', '')
                port_toggles[port_field_name] = {
                    'checkbox': field.get('port_toggle'),
                    'tls_port': field.get('tls_port', ''),
                    'non_tls_port': field.get('non_tls_port', '')
                }
        
        for field in form_fields:
            field_name = field.get('name', '')
            field_type = field.get('type', 'text')
            field_label = field.get('label', field_name)
            field_default = field.get('default', '')
            field_options = field.get('options', [])
            
            # Use saved value if available, otherwise use default
            saved_value = saved_values.get(field_name)
            
            label = QLabel(field_label + ":")
            
            # Set minimum width for form fields (3x default width)
            field_min_width = 400
            
            if field_type == 'text':
                widget = QLineEdit()
                widget.setMinimumWidth(field_min_width)
                if saved_value is not None:
                    widget.setText(str(saved_value))
                elif field_default:
                    widget.setText(str(field_default))
                    
            elif field_type == 'password':
                widget = QLineEdit()
                widget.setMinimumWidth(field_min_width)
                widget.setEchoMode(QLineEdit.Password)
                if saved_value is not None:
                    widget.setText(str(saved_value))
                elif field_default:
                    widget.setText(str(field_default))
                    
            elif field_type == 'checkbox':
                widget = QCheckBox()
                if saved_value is not None:
                    widget.setChecked(bool(saved_value))
                elif field_default:
                    widget.setChecked(bool(field_default))
                    
            elif field_type == 'combo':
                widget = QComboBox()
                widget.setMinimumWidth(field_min_width)
                widget.addItems(field_options)
                if saved_value is not None and saved_value in field_options:
                    widget.setCurrentText(str(saved_value))
                elif field_default and field_default in field_options:
                    widget.setCurrentText(str(field_default))
                    
            elif field_type == 'file':
                # Create a horizontal layout with line edit and browse button
                container = QWidget()
                hlayout = QHBoxLayout(container)
                hlayout.setContentsMargins(0, 0, 0, 0)
                
                line_edit = QLineEdit()
                line_edit.setMinimumWidth(field_min_width - 80)  # Account for Browse button
                if saved_value is not None:
                    line_edit.setText(str(saved_value))
                elif field_default:
                    line_edit.setText(str(field_default))
                
                browse_btn = QPushButton("Browse")
                file_filter = field.get('filter', 'All Files (*)')
                browse_btn.clicked.connect(
                    lambda checked, le=line_edit, ff=file_filter: self.browse_file(le, ff)
                )
                
                hlayout.addWidget(line_edit)
                hlayout.addWidget(browse_btn)
                
                widget = container
                # Store the line edit for value retrieval
                widget._line_edit = line_edit
                
            elif field_type == 'readonly':
                widget = QLineEdit()
                widget.setMinimumWidth(field_min_width)
                widget.setReadOnly(True)
                widget.setStyleSheet("background-color: #f0f0f0; color: #666666;")
                if field_default:
                    widget.setText(str(field_default))
                
            else:
                # Default to text
                widget = QLineEdit()
                if saved_value is not None:
                    widget.setText(str(saved_value))
                elif field_default:
                    widget.setText(str(field_default))
            
            self.ui.formLayout.addRow(label, widget)
            self.form_widgets[module_name][field_name] = widget
        
        # Store port toggle info for this module
        self.port_toggle_map[module_name] = port_toggles
        
        # Second pass: connect TLS checkboxes to port fields
        for port_field_name, toggle_info in port_toggles.items():
            checkbox_name = toggle_info['checkbox']
            tls_port = toggle_info['tls_port']
            non_tls_port = toggle_info['non_tls_port']
            
            if checkbox_name in self.form_widgets[module_name] and port_field_name in self.form_widgets[module_name]:
                checkbox_widget = self.form_widgets[module_name][checkbox_name]
                port_widget = self.form_widgets[module_name][port_field_name]
                
                if isinstance(checkbox_widget, QCheckBox) and isinstance(port_widget, QLineEdit):
                    # Connect the checkbox state change to update the port
                    checkbox_widget.stateChanged.connect(
                        lambda state, pw=port_widget, tp=tls_port, ntp=non_tls_port: 
                            self.on_tls_toggle(state, pw, tp, ntp)
                    )

    def browse_file(self, line_edit, file_filter):
        """Open file dialog and set the path in the line edit."""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", file_filter
        )
        if file_name:
            line_edit.setText(file_name)

    def on_tls_toggle(self, state, port_widget, tls_port, non_tls_port):
        """Update port field when TLS checkbox is toggled."""
        # Qt.Checked = 2, Qt.Unchecked = 0
        if state == Qt.Checked or state == 2:
            if tls_port:
                port_widget.setText(str(tls_port))
        else:
            if non_tls_port:
                port_widget.setText(str(non_tls_port))

    def save_form_values(self):
        """Save current form values for the current module."""
        if not self.current_module:
            return
        
        module_name = self.current_module
        if module_name not in self.form_widgets:
            return
        
        self.form_values[module_name] = {}
        
        for field_name, widget in self.form_widgets[module_name].items():
            if isinstance(widget, QLineEdit):
                self.form_values[module_name][field_name] = widget.text()
            elif isinstance(widget, QCheckBox):
                self.form_values[module_name][field_name] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                self.form_values[module_name][field_name] = widget.currentText()
            elif hasattr(widget, '_line_edit'):  # File browser widget
                self.form_values[module_name][field_name] = widget._line_edit.text()

    def get_form_data(self):
        """Get current form data as a dictionary."""
        if not self.current_module:
            return {}
        
        module_name = self.current_module
        if module_name not in self.form_widgets:
            return {}
        
        form_data = {}
        
        for field_name, widget in self.form_widgets[module_name].items():
            if isinstance(widget, QLineEdit):
                form_data[field_name] = widget.text()
            elif isinstance(widget, QCheckBox):
                form_data[field_name] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                form_data[field_name] = widget.currentText()
            elif hasattr(widget, '_line_edit'):  # File browser widget
                form_data[field_name] = widget._line_edit.text()
        
        return form_data

    def clear_form(self):
        """Reset all form fields to their default values for the current module."""
        if not self.current_module:
            return
        
        module_name = self.current_module
        if module_name not in self.form_widgets:
            return
        
        module = self.modules.get(module_name)
        if not module:
            return
        
        # Build a dict of field defaults
        form_fields = getattr(module, 'form_fields', [])
        defaults = {}
        for field in form_fields:
            field_name = field.get('name', '')
            defaults[field_name] = {
                'default': field.get('default', ''),
                'options': field.get('options', [])
            }
        
        for field_name, widget in self.form_widgets[module_name].items():
            field_default = defaults.get(field_name, {}).get('default', '')
            field_options = defaults.get(field_name, {}).get('options', [])
            
            if isinstance(widget, QLineEdit):
                widget.setText(str(field_default) if field_default else '')
            elif isinstance(widget, QCheckBox):
                widget.setChecked(bool(field_default) if field_default else False)
            elif isinstance(widget, QComboBox):
                if field_default and field_default in field_options:
                    widget.setCurrentText(str(field_default))
                else:
                    widget.setCurrentIndex(0)
            elif hasattr(widget, '_line_edit'):  # File browser widget
                widget._line_edit.setText(str(field_default) if field_default else '')
        
        # Clear saved values too
        self.form_values[module_name] = {}
        
        self.ui.StatusTextBox.appendPlainText("Form reset to defaults")

    def check_authentication(self):
        """Attempt authentication using the current module and form data."""
        if not self.current_module:
            self.ui.StatusTextBox.appendPlainText("Error: No authentication system selected")
            return
        
        module = self.modules.get(self.current_module)
        if not module:
            self.ui.StatusTextBox.appendPlainText("Error: Module not found")
            return
        
        # Get form data
        form_data = self.get_form_data()
        
        # Save form values
        self.save_form_values()
        
        display_name = getattr(module, 'module_description', self.current_module)
        self.ui.StatusTextBox.appendPlainText(f"\n{'='*60}")
        self.ui.StatusTextBox.appendPlainText(f"Checking authentication for: {display_name}")
        self.ui.StatusTextBox.appendPlainText(f"{'='*60}")
        
        try:
            # Call the module's authenticate function
            success, message = module.authenticate(form_data)
            
            if success:
                self.ui.StatusTextBox.appendPlainText(f"[SUCCESS] {message}")
            else:
                self.ui.StatusTextBox.appendPlainText(f"[FAILED] {message}")
                
        except Exception as e:
            self.ui.StatusTextBox.appendPlainText(f"[ERROR] Exception during authentication: {e}")

    def showEvent(self, event):
        """Set focus when the tab is shown."""
        super().showEvent(event)
        self.ui.ModulesList.setFocus()

    def cleanup(self):
        """Clean up resources before closing."""
        # Save current form values
        self.save_form_values()
