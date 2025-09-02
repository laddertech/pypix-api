# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Testing
```bash
# Run mock tests (default)
make test
# Or directly with pytest
pytest tests/tests_mock

# Run integration tests (requires API credentials)
pytest tests/tests_integration
```

### Code Quality
```bash
# Check code style and linting
make lint
# Or directly
ruff check .

# Format code
make format
# Or directly
ruff format .

# Fix linting issues and format
make fix
```

### Building and Publishing
```bash
# Sync dependencies
make sync

# Build package
make build

# Clean previous builds
make clean

# Publish to PyPI (requires credentials)
make publish
```

### Version Management
```bash
# Increment patch version (0.5.0 -> 0.5.1)
make bump-patch

# Increment minor version (0.5.0 -> 0.6.0)
make bump-minor

# Increment major version (0.5.0 -> 1.0.0)
make bump-major
```

## Architecture Overview

This is a Python library for integrating with Brazilian bank APIs, focused on PIX payment system operations.

### Core Components

**Authentication Layer (`pypix_api/auth/`)**
- `oauth2.py`: OAuth2 client implementation for bank API authentication
- `mtls.py`: Mutual TLS authentication support
- Banks require OAuth2Client initialization with client_id, certificate (.pem), and private key (.key)

**Bank Integration Layer (`pypix_api/banks/`)**
- `base.py`: Abstract base class `BankPixAPIBase` that all bank implementations inherit from
- `bb.py`: Banco do Brasil implementation
- `sicoob.py`: Sicoob implementation
- `exceptions.py`: Bank-specific exception classes for error handling

**Method Mixins (`pypix_api/banks/methods/`)**
The base class uses multiple inheritance with method mixins for different PIX operations:
- `cob_methods.py`: Immediate charges (cobranças imediatas)
- `cobv_methods.py`: Charges with due date (cobranças com vencimento)
- `pix_methods.py`: PIX transaction operations (consult, refund)
- `rec_methods.py`: Recurrence operations
- `solic_rec_methods.py`: Recurrence solicitation methods
- `webhook_methods.py`: Webhook configuration
- `webhook_cobr_methods.py`: Charge webhook specific methods
- `webhook_rec_methods.py`: Recurrence webhook specific methods

**Models (`pypix_api/models/`)**
- `pix.py`: PIX data models and structures

**Scopes (`pypix_api/scopes/`)**
- `registry.py`: OAuth2 scope registry system
- Bank-specific scope definitions for API permissions

### Key Design Patterns

1. **Inheritance Structure**: Each bank class inherits from `BankPixAPIBase`, which aggregates all method mixins
2. **OAuth2 Dependency**: Banks are instantiated with an OAuth2Client instance, not credentials directly
3. **Method Organization**: PIX operations are organized into logical groups as separate mixins
4. **Error Handling**: Standardized exception hierarchy for consistent error management across banks

### Adding New Bank Support

To add a new bank:
1. Create a new file in `pypix_api/banks/`
2. Inherit from `BankPixAPIBase`
3. Define `BASE_URL` and `TOKEN_URL` class attributes
4. Override bank-specific methods if needed
5. Add scope definitions in `pypix_api/scopes/`

### Testing Strategy

- **Mock Tests** (`tests/tests_mock/`): Unit tests with mocked API responses
- **Integration Tests** (`tests/tests_integration/`): Real API calls requiring credentials

Always run mock tests before commits. Integration tests require proper `.env` configuration with bank credentials.
