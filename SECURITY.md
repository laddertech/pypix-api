# Security Policy

## Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.5.x   | :white_check_mark: |
| 0.4.x   | :white_check_mark: |
| < 0.4   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in pypix-api, please report it responsibly.

### How to Report

1. **Email**: Send details to [fabio@ladder.dev.br](mailto:fabio@ladder.dev.br)
2. **Subject**: Use "SECURITY: [Brief Description]"
3. **Include**:
   - Detailed description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact assessment
   - Suggested mitigation (if any)

### What NOT to Report Publicly

- Do NOT create GitHub issues for security vulnerabilities
- Do NOT discuss vulnerabilities in public forums
- Do NOT publish exploit code publicly

### Response Timeline

- **Initial Response**: Within 48 hours
- **Assessment**: Within 5 business days
- **Fix Development**: Varies by severity
- **Public Disclosure**: After fix is released

## Security Measures

### Authentication & Authorization
- OAuth2 with mTLS for bank API authentication
- Certificate validation and secure storage
- No credentials stored in code or logs

### Data Protection
- No PII stored or logged by default
- Secure transmission of all sensitive data
- Input validation and sanitization

### Dependencies
- Regular security audits with `bandit`
- Automated dependency updates with Dependabot
- Minimal dependency footprint

## Secure Development Practices

### Code Quality
- Static analysis with Ruff and MyPy
- Pre-commit hooks for security checks
- Automated testing with security scenarios

### CI/CD Security
- Secrets managed through GitHub Secrets
- Trusted publishing to PyPI
- Secure artifact handling

### Configuration
- Environment variables for sensitive config
- Secure defaults for all settings
- Documentation of security considerations

## Known Security Considerations

### Banking API Integration
- **Certificate Management**: Keep mTLS certificates secure and rotate regularly
- **Token Handling**: OAuth2 tokens have limited lifetime and scope
- **Network Security**: Use HTTPS for all API communications

### PIX Transactions
- **Data Validation**: All PIX data is validated before API calls
- **Error Handling**: Sensitive information not exposed in error messages
- **Logging**: Financial data excluded from logs

## Best Practices for Users

### Certificate Security
```python
# ✅ Good: Use environment variables
cert_path = os.getenv('PIX_CERT_PATH')
key_path = os.getenv('PIX_KEY_PATH')

# ❌ Bad: Hardcoded paths
cert_path = '/path/to/cert.pem'
```

### Credential Management
```python
# ✅ Good: Environment variables
client_id = os.getenv('PIX_CLIENT_ID')
client_secret = os.getenv('PIX_CLIENT_SECRET')

# ❌ Bad: Hardcoded credentials
client_id = 'your-client-id'
```

### Error Handling
```python
# ✅ Good: Generic error messages
try:
    result = api.criar_cob(txid, data)
except PixAuthError:
    logger.error('Authentication failed')

# ❌ Bad: Exposing sensitive details
except PixAuthError as e:
    logger.error(f'Auth failed with token: {token}')
```

### Logging Configuration
```python
# ✅ Good: Exclude sensitive data
logging.getLogger('pypix_api').setLevel(logging.INFO)

# Configure to exclude request/response bodies
api = BBPixAPI(oauth=oauth_client, debug=False)
```

## Vulnerability Disclosure Process

### Coordinated Disclosure
1. **Private Report** to security team
2. **Acknowledgment** within 48 hours
3. **Assessment** and severity rating
4. **Fix Development** in collaboration with reporter
5. **Testing** and validation
6. **Release** with security advisory
7. **Public Disclosure** after users have time to update

### Security Advisories
- Published through GitHub Security Advisories
- CVE assignment when applicable
- Clear upgrade path and mitigation steps

## Security Tools & Automation

### Static Analysis
- **Bandit**: Security linting for Python
- **Ruff**: Code quality with security rules
- **MyPy**: Type checking prevents certain vulnerabilities

### Dependency Security
- **Dependabot**: Automated dependency updates
- **pip-audit**: Regular vulnerability scanning
- **SPDX**: Software bill of materials

### CI/CD Security
- **GitHub Security**: Code scanning and secret detection
- **Trusted Publishing**: Secure PyPI releases
- **Artifact Signing**: Verifiable builds

## Compliance & Standards

### Industry Standards
- Follows OWASP Top 10 guidelines
- Implements secure coding practices
- Regular security assessments

### Brazilian Financial Regulations
- Complies with LGPD (Lei Geral de Proteção de Dados)
- Follows BCB (Banco Central) security guidelines
- Implements PIX security requirements

## Contact Information

### Security Team
- **Email**: fabio@ladder.dev.br
- **Response Time**: 48 hours maximum
- **Languages**: Portuguese, English

### Emergency Contact
For critical vulnerabilities requiring immediate attention:
- **Subject Line**: "CRITICAL SECURITY: [Brief Description]"
- **Response Time**: 24 hours

## Recognition

We appreciate security researchers who help improve pypix-api security:

### Hall of Fame
*No vulnerabilities reported yet - be the first to help secure pypix-api!*

### Recognition Policy
- Public acknowledgment in release notes (with permission)
- Credit in security advisories
- Contribution recognition in project documentation

## Legal

### Safe Harbor
We commit to:
- Not pursuing legal action against security researchers
- Working collaboratively to resolve issues
- Providing credit for responsible disclosure

### Scope
This policy covers:
- pypix-api source code and dependencies
- Official documentation and examples
- CI/CD infrastructure and workflows

Out of scope:
- Third-party integrations
- User-specific implementations
- Banking partner systems

---

**Last Updated**: September 1, 2025
**Version**: 1.0

For questions about this security policy, contact: [fabio@ladder.dev.br](mailto:fabio@ladder.dev.br)
