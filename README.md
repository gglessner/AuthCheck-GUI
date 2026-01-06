# AuthCheck Module

The `AuthCheck` module is a component of the **HACKtiveMQ Suite** and **ningu framework**, designed to test authentication against various systems including message brokers, databases, directory services, and more.

## Overview

The `AuthCheck` module enables users to:

* Select from multiple authentication system types via a dynamic list
* Fill out system-specific authentication forms with appropriate fields
* Test authentication and view results in a status window
* Easily add new authentication modules for additional systems

The module dynamically loads authentication modules from `modules/AuthCheck_modules/`, which are created automatically if they do not exist.

## Requirements

### Software

* **Python**: Version 3.8 or later recommended.
* **Operating System**: Compatible with Windows, Linux, and macOS.

### Python Dependencies

The following Python packages are required, as specified in `requirements.txt`:

```
PySide6>=6.0.0
```

Optional dependencies for specific authentication modules:
```
kafka-python        # Apache Kafka
redis               # Redis
pymqi               # IBM MQ (requires MQ client libraries)
oracledb            # Oracle Database
ibm_db              # IBM DB2
psycopg2-binary     # PostgreSQL
mysql-connector-python  # MySQL/MariaDB
ldap3               # LDAP/Active Directory
paramiko            # SSH
solace-pubsubplus   # Solace PubSub+
```

## Installation

1. **Obtain the Module**:
   * The `AuthCheck` module is part of the HACKtiveMQ Suite. Clone or download the repository.

2. **Install Python Dependencies**:
   * Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   .\venv\Scripts\activate     # On Windows
   source venv/bin/activate    # On Linux/macOS
   ```
   * Install the required packages:
   ```
   pip install -r requirements.txt
   ```
   * Install optional packages for specific authentication types as needed.

## Usage

1. **Launch the Module**:
   * Run the `AuthCheck` module via the ningu framework or the HACKtiveMQ Suite.

2. **Select Authentication System**:
   * Click on an authentication system from the list on the left side.
   * The appropriate form fields will appear on the right side.

3. **Fill Out the Form**:
   * Enter the required connection and authentication details.
   * Use checkboxes for options like TLS/SSL.
   * Use the Browse button to select certificate or key files.

4. **Test Authentication**:
   * Click the **Check** button to attempt authentication.
   * Results will appear in the **Status** window at the bottom.
   * Success or failure messages with details will be displayed.

5. **Clear Form**:
   * Click the **Clear** button to reset all form fields.
   * Form values are remembered when switching between systems.

## Directory Structure

```
AuthCheck-GUI/
├── 5_AuthCheck.py              # Main AuthCheck module
├── AuthCheck_modules/          # Authentication sub-modules
│   ├── Apache_Kafka.py
│   ├── DB2.py
│   ├── IBM_MQ.py
│   ├── LDAP.py
│   ├── MySQL.py
│   ├── Oracle_DB.py
│   ├── PostgreSQL.py
│   ├── Redis.py
│   ├── Solace_PubSub.py
│   ├── SSH.py
│   └── ...
├── AuthCheck_module_libs/      # Shared library modules
│   └── auth_utils.py
├── requirements.txt
├── LICENSE
└── README.md
```

## Creating Custom Authentication Modules

Each authentication module must be a `.py` file in `modules/AuthCheck_modules/` with:

1. **`module_description`**: Display name for the authentication system
2. **`form_fields`**: List of field definitions
3. **`authenticate(form_data)`**: Function that returns `(success: bool, message: str)`

### Example Module:

```python
module_description = "My Custom System"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "1234"},
    {"name": "use_tls", "type": "checkbox", "label": "Enable TLS"},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", 
     "options": ["Password", "Certificate"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "cert_file", "type": "file", "label": "Certificate", 
     "filter": "Certificate Files (*.pem *.crt);;All Files (*)"},
]

def authenticate(form_data):
    host = form_data.get('host', '')
    # ... perform authentication ...
    if success:
        return True, "Authentication successful!"
    else:
        return False, "Authentication failed: reason"
```

### Field Types:

| Type | Widget | Description |
|------|--------|-------------|
| `text` | QLineEdit | Standard text input |
| `password` | QLineEdit (hidden) | Password input with masked characters |
| `checkbox` | QCheckBox | Boolean toggle |
| `combo` | QComboBox | Dropdown with `options` list |
| `file` | QLineEdit + Browse | File path with file dialog, uses `filter` |

### Field Properties:

| Property | Required | Description |
|----------|----------|-------------|
| `name` | Yes | Field identifier (used in form_data) |
| `type` | Yes | Widget type (text, password, checkbox, combo, file) |
| `label` | Yes | Display label |
| `default` | No | Default value |
| `options` | combo only | List of dropdown options |
| `filter` | file only | File dialog filter string |

## Included Authentication Modules

* **Apache Kafka** - SASL/SSL authentication
* **Solace PubSub+** - Basic/Certificate authentication
* **Redis** - Password and ACL authentication
* **IBM MQ** - User/Password and Certificate authentication
* **Oracle Database** - Standard and privileged connections
* **IBM DB2** - User authentication with SSL
* **PostgreSQL** - Password and SSL certificate authentication
* **MySQL/MariaDB** - Password and SSL authentication
* **LDAP/Active Directory** - Simple, NTLM, and Kerberos
* **SSH** - Password and key-based authentication

## Troubleshooting

* **Module Not Loading**:
  * Ensure the module file is in `modules/AuthCheck_modules/`
  * Check that `form_fields` and `authenticate` are defined
  * Check the Status window for error messages

* **Missing Dependencies**:
  * Install the required package for the authentication type
  * Check error messages for specific pip install commands

* **Connection Failures**:
  * Verify host and port are correct
  * Check firewall and network connectivity
  * Verify TLS/SSL settings match server configuration

## License

This module is licensed under the **GNU General Public License v3.0**. See the LICENSE file for details.

## Contact

For issues, questions, or suggestions, contact Garland Glessner at gglessner@gmail.com.
