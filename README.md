# Ningu Framework - AuthCheck Module

**Author:** Garland Glessner  
**License:** [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html)

---

## Overview

**AuthCheck** is a comprehensive authentication testing module for the **Ningu** penetration testing framework. It provides a GUI for testing credentials against **715 different services and systems** commonly found in enterprise environments.

---

## Features

- **715 Authentication Systems** - Databases, message queues, cloud platforms, identity providers, ERP, retail/POS, ICS/SCADA, healthcare, financial, telephony/PBX, video surveillance, ATMs, education, BMC/server management, NAS, VPN, physical access control, building management, and more
- **Dynamic Form Generation** - Each system has its own customized form with relevant fields
- **Real-time Filtering** - Quickly find systems by typing in the filter box
- **Form Persistence** - Values are retained when switching between systems
- **Hints System** - Default credentials and helpful tips displayed for each system
- **TLS Port Toggle** - Automatic port switching for TLS-enabled connections

---

## Installation

1. Place `5_AuthCheck.py` in the `modules/` directory of your Ningu framework installation
2. Place the `AuthCheck_modules/` folder in the `modules/` directory
3. Place the `AuthCheck_module_libs/` folder in the `modules/` directory
4. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Directory Structure

```
modules/
  5_AuthCheck.py              # Main AuthCheck module
  AuthCheck_modules/          # 715 authentication submodules
    Apache_Kafka.py
    AWS_IAM.py
    Dell_iDRAC.py
    Synology_DSM.py
    ...
  AuthCheck_module_libs/      # Shared utilities
    auth_utils.py
```

---

## Usage

1. Launch the Ningu framework
2. Select the "AuthCheck" tab
3. Use the filter box to find your target system (e.g., type "redis" to find Redis)
4. Select a system from the list
5. Fill in the authentication details
6. Click "Check" to test the credentials
7. Results appear in the status window at the bottom

---

## Supported Systems (715 Total)

### BMC / Server Management (4)
Dell iDRAC, HP iLO, Lenovo XCC/IMM, Supermicro IPMI

### NAS Devices (7)
Synology DSM, QNAP QTS, TrueNAS/FreeNAS, Asustor ADM, WD My Cloud, Buffalo TeraStation/LinkStation, Drobo

### VPN / Remote Access (12)
OpenVPN Access Server, WireGuard, Cisco ASA/ASDM, SonicWall, Pulse Secure/Ivanti, Palo Alto GlobalProtect, Cisco AnyConnect, Fortinet SSL VPN, Citrix NetScaler Gateway, F5 BIG-IP APM, Zscaler ZPA, Cloudflare Access

### Physical Access Control (4)
Lenel OnGuard, S2 NetBox, HID VertX/Edge, Gallagher Command Centre

### Building Management Systems (6)
Johnson Controls Metasys, Schneider EcoStruxure, Honeywell EBI, Tridium Niagara, Siemens Desigo CC, OSIsoft PI

### KVM / Out-of-Band Management (5)
Raritan KVM, Avocent/Vertiv KVM, ATEN KVM, Teradici PCoIP, Parsec

### PDU / Power Management (4)
APC PDU/UPS, Raritan PDU, Eaton PDU/UPS, CyberPower PDU/UPS

### Console Servers (3)
Digi Console Server, Opengear Console Server, Lantronix SLC

### Time Servers (1)
Meinberg LANTIME

### Databases - Relational (30+)
PostgreSQL, MySQL, MariaDB, Oracle DB, Microsoft SQL Server, IBM DB2, SAP HANA, Teradata, Sybase ASE, Snowflake, Databricks, Amazon Redshift, Vertica, Greenplum, CockroachDB, ClickHouse, TimescaleDB, YugabyteDB, TiDB, SingleStore (MemSQL), Google Cloud SQL, Google Cloud Spanner, PlanetScale, Supabase, CrateDB, Vitess, Exasol, VoltDB, NuoDB

### Databases - NoSQL & Document (15+)
MongoDB, Amazon DocumentDB, CouchDB, Couchbase, RethinkDB, RavenDB, MarkLogic, Firebase, FaunaDB, ArangoDB, OrientDB

### Databases - Graph (7)
Neo4j, Amazon Neptune, JanusGraph, OrientDB, Dgraph, TigerGraph, ArangoDB

### Databases - Vector (AI/ML) (5)
Pinecone, Weaviate, Qdrant, Milvus, Chroma

### Databases - Time Series (5)
InfluxDB, QuestDB, TDengine, VictoriaMetrics, TimescaleDB

### Databases - Key-Value & Cache (5)
Redis, Memcached, Aerospike, etcd, Hazelcast

### Data Lakehouse & Analytics (3)
Dremio, Databricks, Apache Druid

### Data Catalogs (3)
DataHub, Alation, Collibra

### Message Queues & Streaming (20+)
Apache Kafka, RabbitMQ, Apache ActiveMQ (OpenWire/STOMP/AMQP), IBM MQ, Solace PubSub+, Apache Pulsar, NATS, MQTT, Apache Qpid, TIBCO EMS, Apache Zookeeper, Azure Service Bus, Azure Event Hubs, Google Cloud Pub/Sub, Redpanda, Apache RocketMQ, NSQ, EMQX, VerneMQ, ZeroMQ, Beanstalkd, Memphis, Celery, Temporal, Camunda

### Wireless Access Points (19)
Aruba Instant, Aruba Central, Ruckus Wireless, TP-Link Omada, Fortinet FortiAP, EnGenius Cloud, Cambium Networks, Mist/Juniper, Zyxel Nebula, D-Link Nuclias, Netgear Insight, OpenWrt, Extreme WiNG, Draytek, Cisco Meraki, Ubiquiti UniFi

### Printers (15)
HP LaserJet/OfficeJet, Xerox CentreWare, Canon imageRUNNER, Ricoh Web Image Monitor, Konica Minolta PageScope, Brother Web Based Management, Epson EpsonNet, Lexmark, Kyocera Command Center, Sharp MX, Zebra Label Printers, Toshiba e-STUDIO TopAccess, OKI, CUPS, HP Web Jetadmin

### Industrial Control Systems (ICS/SCADA) (11)
Modbus TCP/RTU, OPC UA, DNP3, Siemens S7, Allen-Bradley/Rockwell, BACnet, EtherNet/IP, PROFINET, Johnson Controls Metasys, Schneider EcoStruxure, OSIsoft PI

### Healthcare Systems (7)
HL7 FHIR, DICOM, Epic, Cerner, Meditech, Allscripts, athenahealth

### Financial/Trading Systems (81)

**Core Banking:** Infosys Finacle, Oracle FLEXCUBE, TCS BaNCS, Mambu, Thought Machine Vault, Temenos T24/Transact, Finastra Fusion, FIS Profile, Jack Henry (SilverLake, CIF 20/20, Symitar), Fiserv (DNA, Precision, Premier, Signature)

**Digital Banking:** Q2, Backbase, Alkami, nCino

**Wealth Management:** Avaloq, FNZ, SEI, SS&C Advent (Geneva, APX, Moxy, Axys), Pershing/NetX360

**Mortgage & Lending:** Ellie Mae Encompass (ICE), Black Knight (MSP, LoanSphere), Blend

**Trading Platforms & EMS/OMS:** ION Trading (Fidessa), Trading Technologies, CQG, FlexTrade, SS&C Eze, Itiviti/Broadridge, Tora, State Street Alpha

**Investment Management:** Charles River IMS, SimCorp Dimension, BlackRock Aladdin, SunGard/FIS APT

**Risk Analytics:** Murex MX.3, Calypso, Numerix, MSCI Barra, Axioma/Qontigo

**Market Data & Infrastructure:** Refinitiv Elektron, Corvil, Exegy, Activ Financial, SIX Financial, Bloomberg Terminal, Refinitiv/Reuters

**Regulatory Reporting:** AxiomSL, Wolters Kluwer OneSumX, Moody's Analytics

**Surveillance & Compliance:** Nasdaq Surveillance (SMARTS)

**Payment Processing:** TSYS (Global Payments), ACI Postilion, FIS CONNEX

**Exchanges & Clearing:** CME Group, ICE, DTCC, Broadridge

**Custody & Asset Servicing:** Northern Trust Matrix, BNY Mellon (Eagle, Nexen), Pershing

**AML/Fraud Detection:** NICE Actimize, SAS AML, Verafin

**Treasury Management:** Kyriba, GTreasury

**Payment Gateways:** Adyen, Worldpay, Square, Braintree, Authorize.Net, Stripe, PayPal

**Financial Data Aggregation:** Plaid, Yodlee

**Credit Bureaus:** Experian, Equifax, TransUnion

**Wire Transfer & Payments:** Fedwire, NACHA/ACH, Visa Direct, Mastercard, FIX Protocol, SWIFT Alliance

**Retail Brokerage APIs:** Interactive Brokers, TD Ameritrade/Schwab, Alpaca, Tradier

**Market Data Vendors:** IHS Markit/S&P Global, FactSet, Morningstar

### Email Security & Archiving (5)
Proofpoint, Mimecast, Barracuda, Global Relay, Smarsh

### Data Loss Prevention (4)
Symantec DLP, Digital Guardian, Forcepoint DLP, Microsoft Defender for Endpoint

### Mobile Device Management (5)
Microsoft Intune, VMware Workspace ONE, Jamf Pro, Ivanti/MobileIron, Kandji

### HR & Payroll Systems (7)
ADP, SAP SuccessFactors, UKG (Kronos/Ultimate), BambooHR, Ceridian Dayforce, Paylocity, Workday

### Physical Security (5)
Genetec Security Center, Milestone XProtect, Lenel OnGuard, HID VertX/Edge, CCure

### Video Surveillance (12)
Axis Communications, Hikvision, Dahua, Avigilon, Hanwha (Samsung), Verkada, Rhombus, ONVIF, Uniview, Bosch Video

### Document Management & eSignature (8)
DocuSign, Adobe Sign (Acrobat Sign), OpenText (Content Server, Documentum), M-Files, SharePoint, Box, HelloSign (Dropbox Sign), PandaDoc

### Endpoint Protection (6)
Trend Micro (Vision One, Apex One, Deep Security), Sophos (Central, XG), ESET PROTECT, Bitdefender GravityZone, Webroot, Kaspersky Security Center

### ATMs & Cash Handling (33)
**ATMs:** NCR (APTRA, NDC, ITM), Diebold Nixdorf (Agilis, DDC), Hyosung (Nautilus), Triton, Genmega, Hantle/Tranax, Fujitsu, OKI, Hitachi-Omron, GRGBanking
**ATM Software:** KAL Kalignite, Auriga WWS
**Payment Switches:** ACI Postilion, FIS CONNEX
**ATM Networks:** PULSE (Discover), STAR (First Data), Allpoint (Cardtronics)
**Payment HSMs:** Thales payShield, Futurex, Utimaco Atalla
**Teller Cash Recyclers:** Glory (GLR-100, RBG-100), Cummins Allison (JetScan), De La Rue (Talaris)
**Payment Terminals:** Verifone (Engage, VHQ, VX/MX), Ingenico (Axium, Desk, Move), PAX (A/E/S-Series)
**Smart Safes:** Tidel, Loomis SafePoint, Brinks CompuSafe
**Cash Management:** INETCO Insight, Prosegur Cash, Fiserv CashComplete

### Education & LMS (7)
Canvas, Blackboard Learn, Moodle, D2L Brightspace, Schoology, PowerSchool SIS, Ellucian Banner

### CRM Systems (8)
Salesforce, Zoho CRM, SugarCRM, Pipedrive, Freshsales, HubSpot, ServiceNow, Zendesk

### Construction & Engineering (3)
Procore, Autodesk BIM 360/ACC, PlanGrid

### Hospitality & Travel (4)
Oracle Opera PMS, Amadeus GDS, Sabre GDS, Travelport (Galileo/Apollo/Worldspan)

### Fleet Management (3)
Samsara, Geotab, Verizon Connect (Fleetmatics)

### Print Management (2)
PaperCut MF/NG, PrinterLogic

### Real Estate & Property (3)
Yardi Voyager, RealPage OneSite, AppFolio

### Insurance (4)
Duck Creek, Majesco, Applied Epic, Guidewire

### Legal & Compliance (2)
Relativity (eDiscovery), OneTrust (Privacy)

### ERP Systems (22)
**SAP:** S/4HANA, ECC, Business One, Retail, Ariba
**Oracle:** E-Business Suite, Fusion Cloud, JD Edwards, PeopleSoft, Retail
**Microsoft:** Dynamics 365 (Finance & Operations, Business Central)
**Other:** NetSuite, Infor (CloudSuite, LN, M3), Epicor (Kinetic), Sage (Intacct, X3), Workday, IFS, Acumatica, SYSPRO, Unit4 (Agresso), Odoo, ERPNext

### Retail & E-commerce (16)
**POS Systems:** Oracle MICROS, NCR Aloha, NCR Counterpoint, Toast, Clover, Revel, Vend/Lightspeed
**E-commerce:** Shopify, BigCommerce, WooCommerce, Magento/Adobe Commerce, PrestaShop
**Supply Chain:** Manhattan Associates, Blue Yonder (JDA)

### Procurement (3)
SAP Ariba, Coupa, Jaggaer

### Accounting (8)
QuickBooks, Xero, FreshBooks, Zoho Books, Wave, Sage Intacct

### Payments (4)
Stripe, PayPal, Square, Clover

### Workforce Management (1)
Kronos/UKG

### Security & SIEM (18)
IBM QRadar, Microsoft Sentinel, CrowdStrike Falcon, VMware Carbon Black, SentinelOne, Qualys, Tenable.io/Nessus, Wazuh, Rapid7 InsightVM, Splunk, Dynatrace, Datadog, LogRhythm, Exabeam, Securonix, ArcSight, Snyk, Checkmarx, Veracode

### Apache Ecosystem (50+)
Hadoop HDFS, Spark, Flink, Hive, HBase, NiFi, Druid, Pinot, Kylin, Impala, Kudu, Phoenix, Solr, Nutch, Tika, BookKeeper, Airflow, Oozie, Livy, Beam, Samza, Knox, Ranger, Shiro, Syncope, Directory, Ambari, Atlas, Zeppelin, Ignite, Geode, Mesos, Storm, Helix, Tomcat, HTTP Server, Karaf, CXF, Camel, Traffic Server, OFBiz, Guacamole, CloudStack, OpenMeetings, OpenWhisk, Doris, Drill, Flume, SkyWalking

### Cloud - AWS (18)
IAM, S3, RDS, DynamoDB, SQS, SNS, Lambda, EC2, EKS, CloudWatch, Secrets Manager, Kinesis, Glue, Neptune, DocumentDB, API Gateway, IoT Core, Greengrass

### Cloud - Azure (11)
Azure AD/Entra ID, Key Vault, Blob Storage, SQL Database, Cosmos DB, Sentinel, DevOps, Service Bus, Event Hubs, IoT Hub, IoT Edge

### Cloud - Google (7)
GCP, Cloud Storage, BigQuery, Pub/Sub, Google Drive, Cloud Spanner, Cloud IoT

### Cloud - Other (6)
DigitalOcean, Linode, Heroku, Vercel, Cloudflare

### Identity & Access Management (16)
LDAP, Okta, Auth0, OneLogin, JumpCloud, Duo Security, PingIdentity, CyberArk, SailPoint, Keycloak, HashiCorp Vault, HashiCorp Consul, Apache Directory, Apache Syncope, Apache Shiro, Teleport

### Virtualization (5)
VMware vSphere/ESXi, Proxmox VE, oVirt/RHEV, Citrix Hypervisor, Nutanix Prism

### Container & Orchestration (7)
Kubernetes, Docker Swarm, OpenShift, HashiCorp Nomad, Portainer, Harbor, Rancher

### Service Mesh (3)
Istio, Linkerd, Consul Connect

### API Gateways (8)
Kong, Apigee, AWS API Gateway, Tyk, Traefik, Apache APISIX, Gravitee, Ambassador

### Edge Computing & IoT (6)
AWS Greengrass, Azure IoT Edge, CoAP, LwM2M, Zigbee/Zigbee2MQTT, Thread/OpenThread

### CI/CD & DevOps (18)
Jenkins, GitLab, GitHub, Bitbucket, Azure DevOps, CircleCI, TeamCity, Bamboo, ArgoCD, Nexus, Artifactory, SonarQube, Harbor, Terraform Cloud, Ansible AWX, Spinnaker, Octopus Deploy, Flux CD

### Configuration Management (4)
Puppet Enterprise, Chef Automate, SaltStack, Ansible AWX

### Secrets & Key Management (8)
HashiCorp Vault, AWS Secrets Manager, Doppler, Voltage SecureData, Thales CipherTrust, Fortanix DSM, Akeyless Vault, Venafi TPP

### Networking & Firewalls (24)
Cisco ISE, Cisco Meraki, F5 BIG-IP, Palo Alto Networks, Fortinet FortiGate, Check Point, Citrix ADC, Juniper Networks, Arista Networks, Ubiquiti UniFi, Kong, HAProxy, NGINX, Traefik, Envoy, Cloudflare, Teleport, pfSense, OPNsense, MikroTik RouterOS, Sophos Central

### Application Servers & Middleware (25+)
WildFly, WebLogic, WebSphere, GlassFish, Apache Tomcat, NGINX, HAProxy, Traefik, Envoy, Apache Zookeeper, etcd, Consul, Apache Karaf, Apache Camel, Apache CXF, Apache HTTP Server, Apache Traffic Server, Caddy, Jetty, Apache APISIX, Gravitee, Varnish, Spring Cloud Gateway, Squid, Ambassador

### Logging & Observability (22)
Splunk, Dynatrace, AppDynamics, New Relic, Datadog, Prometheus, Grafana, Grafana Loki, Jaeger, Zipkin, Graylog, Zabbix, Nagios, Sumo Logic, Icinga, Checkmk, LibreNMS, PRTG, Honeycomb, Lightstep, Vector, Cribl, Fluentd, Logstash

### Collaboration & Productivity (14)
Slack, Microsoft Teams, Cisco Webex, Zoom, Asana, Trello, Notion, Airtable, Dropbox, Box, OneDrive, Basecamp, Discord, Twitch

### Project Management (5)
Monday.com, ClickUp, Wrike, Smartsheet, Jira

### Business Intelligence (4)
Tableau Server, Power BI, Looker, Metabase

### Service Management (3)
ServiceNow, Zendesk, PagerDuty

### API Management (5)
Google Apigee, Kong, AWS API Gateway, Tyk, Traefik

### Communication (3)
Twilio, SendGrid, Cisco Webex

### Payment & CRM (4)
Stripe, PayPal, HubSpot, Mailchimp

### Enterprise Storage (5)
NetApp ONTAP, NetApp SAN/E-Series, Pure Storage, Dell EMC PowerStore, MinIO

### Backup & Recovery (5)
Veeam, Commvault, Rubrik, Cohesity, Veritas NetBackup

### Enterprise Applications (8)
SAP, Salesforce, Workday, Informatica, MuleSoft, Jira, Confluence, SharePoint

### Remote Access Protocols (3)
SSH, FTP, SMB

### Network Management (1)
SNMP (v1/v2c/v3)

### Telephony & PBX (15)
Cisco CUCM, Cisco Unity Connection, Asterisk/FreePBX, Avaya Communication Manager, Avaya Aura Session Manager, 3CX, Mitel MiVoice, Genesys Cloud, SIP (Generic), RingCentral, Vonage (Nexmo), Sangoma PBX, Yealink, Grandstream UCM

### Mainframe & Legacy (5)
IBM z/OS, IBM CICS, IBM IMS, TSO/ISPF, VTAM/SNA

### Embedded & Real-Time OS (2)
VxWorks, QNX

### Media Servers (3)
Plex, Emby, Jellyfin

### Gaming Platforms (5)
Steam API, Epic Games, PlayStation Network, Xbox Live, Twitch

---

## Adding New Modules

Create a new `.py` file in `AuthCheck_modules/` with:

```python
module_description = "Display Name (Category)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8080",
     "port_toggle": "use_ssl", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", 
     "options": ["Basic", "Token"], "default": "Basic"},
    {"name": "hints", "type": "readonly", "label": "Hints", 
     "default": "Default credentials: admin / admin"},
]

def authenticate(form_data):
    """Returns: (success: bool, message: str)"""
    # ... authentication logic ...
    return True, "Success message"
```

### Field Types

| Type | Description |
|------|-------------|
| `text` | Standard text input |
| `password` | Password input (masked) |
| `checkbox` | Boolean toggle |
| `combo` | Dropdown (requires `options` list) |
| `file` | File browser |
| `readonly` | Read-only text (for hints) |

### TLS Port Toggle

Add `port_toggle` to automatically switch ports based on TLS checkbox:

```python
{"name": "port", "type": "text", "label": "Port", "default": "8080",
 "port_toggle": "use_ssl", "tls_port": "8443", "non_tls_port": "8080"},
```

---

## Module Categories

All modules include a category tag in their description for easy filtering:

| Tag | Category |
|-----|----------|
| (DB) | Databases |
| (MQ) | Message Queues |
| (Middleware) | Application Servers & Middleware |
| (IAM) | Identity & Access Management |
| (Security) | Security Tools & SIEM |
| (Monitoring) | Monitoring & Observability |
| (CI/CD) | DevOps & CI/CD |
| (Cloud) | Cloud Platforms |
| (Container) | Container & Orchestration |
| (Network) | Networking & Firewalls |
| (VPN) | VPN & Remote Access |
| (BMC) | Server Management / BMC |
| (NAS) | Network Attached Storage |
| (Power) | PDU & UPS |
| (Console) | Console Servers |
| (Access Control) | Physical Access Control |
| (BMS) | Building Management |
| (KVM) | KVM Switches |
| (ICS) | Industrial Control Systems |
| (Healthcare) | Healthcare Systems |
| (Financial) | Financial & Trading |
| (ATM) | ATMs & Cash Handling |
| (PBX) | Telephony & VoIP |
| (Video) | Video Surveillance |
| (ERP) | ERP Systems |
| (CRM) | CRM Systems |
| (HR) | HR & Payroll |
| (LMS) | Education & LMS |
| (Printer) | Printers |

---

## License

GNU GPL v3.0 - see [LICENSE](https://www.gnu.org/licenses/gpl-3.0.html)

---

## Contact

Garland Glessner - gglessner@gmail.com
