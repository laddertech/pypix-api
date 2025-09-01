# Security Policy for pypix-api

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.5.x   | :white_check_mark: |
| 0.4.x   | :white_check_mark: |
| < 0.4   | :x:                |

## Security Standards

### Development Security
- All code changes go through security review
- Automated security scanning on every commit
- Dependency vulnerability monitoring
- Secret scanning and prevention

### Runtime Security
- Secure defaults for all configurations
- Input validation and sanitization
- Secure credential handling
- TLS encryption for all communications

## Security Testing

We employ multiple layers of security testing:

### 1. Static Analysis Security Testing (SAST)
- **Bandit**: Python security linter
- **Semgrep**: Pattern-based security analysis
- **CodeQL**: GitHub's semantic code analysis
- **Ruff**: Security-focused linting rules

### 2. Dependency Security
- **pip-audit**: Python package vulnerability scanner
- **Safety**: Database of known security vulnerabilities
- **Dependabot**: Automated dependency updates
- **License compliance**: Ensuring compatible licenses

### 3. Secret Detection
- **TruffleHog**: Secret scanning with verification
- **GitLeaks**: Pattern-based secret detection
- **Pre-commit hooks**: Local secret prevention
- **GitHub secret scanning**: Platform-level protection

### 4. Security Scorecard
- **OpenSSF Scorecard**: Comprehensive security assessment
- **Best practices**: Following industry standards
- **Continuous monitoring**: Regular security posture evaluation

## Vulnerability Response

### Reporting Timeline
- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 5 business days
- **Resolution**: Varies by severity (see below)
- **Public Disclosure**: After fix is available

### Severity Classification

#### Critical (CVSS 9.0-10.0)
- **Response Time**: 24 hours
- **Resolution Time**: 7 days
- **Examples**: Remote code execution, authentication bypass

#### High (CVSS 7.0-8.9)
- **Response Time**: 48 hours
- **Resolution Time**: 14 days
- **Examples**: Privilege escalation, data disclosure

#### Medium (CVSS 4.0-6.9)
- **Response Time**: 1 week
- **Resolution Time**: 30 days
- **Examples**: Information disclosure, denial of service

#### Low (CVSS 0.1-3.9)
- **Response Time**: 2 weeks
- **Resolution Time**: Next release cycle
- **Examples**: Minor information leaks, logging issues

## Security Controls

### Authentication & Authorization
- OAuth2 with mTLS for bank API authentication
- Certificate validation and secure storage
- Scope-based access control
- Token lifecycle management

### Data Protection
- No PII stored by default
- Secure data transmission
- Input validation and sanitization
- Logging exclusion of sensitive data

### Infrastructure Security
- Secure CI/CD pipelines
- Dependency scanning
- Secret management
- Least privilege access

## Secure Development Guidelines

### Code Security
```python
# ✅ Good: Parameterized queries
cursor.execute("SELECT * FROM table WHERE id = %s", [user_id])

# ❌ Bad: String concatenation
cursor.execute("SELECT * FROM table WHERE id = " + user_id)
```

### Credential Management
```python
# ✅ Good: Environment variables
client_id = os.getenv('PIX_CLIENT_ID')

# ❌ Bad: Hardcoded values
client_id = 'abc123'
```

### Error Handling
```python
# ✅ Good: Generic error messages
logger.error('Authentication failed')

# ❌ Bad: Exposing sensitive details
logger.error(f'Login failed for user {username} with token {token}')
```

### HTTPS Enforcement
```python
# ✅ Good: Always use HTTPS
response = requests.get('https://api.example.com', verify=True)

# ❌ Bad: HTTP or disabled certificate verification
response = requests.get('http://api.example.com')
response = requests.get('https://api.example.com', verify=False)
```

## Security Testing Commands

### Local Security Testing
```bash
# Run security linter
bandit -r pypix_api/ -ll

# Check for vulnerabilities
pip-audit --desc --format=json

# Scan for secrets
git secrets --scan

# Run all security checks
make security-scan
```

### CI/CD Security
- All PRs trigger security scans
- Failed security checks block merging
- Weekly comprehensive security audits
- Automated dependency updates

## Incident Response

### Security Incident Process
1. **Detection**: Automated monitoring and reporting
2. **Assessment**: Severity classification and impact analysis
3. **Containment**: Immediate mitigation measures
4. **Investigation**: Root cause analysis
5. **Resolution**: Permanent fix implementation
6. **Recovery**: Service restoration and validation
7. **Lessons Learned**: Process improvement

### Communication
- Security incidents are handled privately
- Public disclosure only after resolution
- User notification for data breaches
- Transparency in post-incident reports

## Compliance

### Standards Adherence
- OWASP Top 10 compliance
- NIST Cybersecurity Framework alignment
- ISO 27001 principles adoption
- Industry best practices implementation

### Brazilian Regulations
- LGPD (Lei Geral de Proteção de Dados) compliance
- BCB (Banco Central do Brasil) security requirements
- PIX security standards adherence
- Financial services regulations

## Security Resources

### Documentation
- [OWASP Python Security](https://owasp.org/www-project-python-security/)
- [Python Security Best Practices](https://python.org/dev/security/)
- [PIX Security Guide](https://www.bcb.gov.br/pix)

### Tools
- [Bandit Security Linter](https://bandit.readthedocs.io/)
- [Safety Security Scanner](https://safety.readthedocs.io/)
- [Semgrep SAST](https://semgrep.dev/)

### Training
- Secure coding practices
- Threat modeling workshops
- Security incident response drills
- Regular security awareness updates

## Contact

### Security Team
- **Primary**: fabio@ladder.dev.br
- **Emergency**: Use GitHub Security tab
- **Response SLA**: 48 hours maximum

### Bug Bounty
Currently not available, but considering implementation for v1.0.

---

**This security policy is reviewed quarterly and updated as needed.**

Last updated: September 1, 2025
