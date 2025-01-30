# python setup.py build
-- to build the .exe

#### **1. Core Scanning Enhancements**
| Feature                     | Status    | Priority | Details                                                                 |
|-----------------------------|-----------|----------|-------------------------------------------------------------------------|
| **ML Integration**          | Partial   | High     | Expand `MLScanner` to flag anomalies in: <br> - Process trees <br> - Unusual port combinations |
| **Third-Party API Support** | New       | Medium   | Add Nessus API integration (user-provided keys) for credentialed scans |

#### **2. Reporting & Compliance**
| Feature                     | Status    | Priority | Details                                                                 |
|-----------------------------|-----------|----------|-------------------------------------------------------------------------|
| **PDF Reports**             | New       | High     | Use `reportlab` to generate PDF reports with: <br> - Executive summary <br> - Visual charts |
| **Legal Safeguards**        | New       | Critical | Add: <br> - GPL compliance check (block OpenVAS code) <br> - API terms popup for Nessus/Metasploit users |
| **Log Retention**           | New       | Medium   | Store logs in `./logs/` with rotation (7 days)                          |

#### **3. UI/UX Improvements**
| Feature                     | Status    | Priority | Details                                                                 |
|-----------------------------|-----------|----------|-------------------------------------------------------------------------|
| **Interactive CLI**         | Partial   | High     | Add: <br> - Scan profile selection (quick/deep) <br> - Pause/resume functionality |
| **Dashboard Lite**          | New       | Medium   | ASCII-based dashboard showing: <br> - Real-time risk score <br> - Top vulnerabilities |

#### **4. Automation & Testing**
| Feature                     | Status    | Priority | Details                                                                 |
|-----------------------------|-----------|----------|-------------------------------------------------------------------------|
| **Scheduled Scans**         | New       | Medium   | Add `cron`-like scheduler for daily scans                               |
| **Unit Tests**              | Partial   | High     | Cover: <br> - Report generation <br> - Nessus API integration <br> - Logging |

---

### **Post-MVP Features (Post-Feb 25 Launch)**
1. **Zero-Day Detection**: Autoencoder model trained on exploit-db data.
2. **Container Scanning**: Integrate Trivy (Apache-2.0 license) for Docker/K8s checks.
3. **Active Response**: Automated firewall rule updates for critical vulnerabilities.
4. **Web Dashboard**: React-based UI with historical trend analysis.
