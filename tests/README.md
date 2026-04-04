# Master Dashboard Template - Testing Guide

Comprehensive testing suite for the master-dashboard-template.

---

## 🎯 **What We Test**

This test suite validates:
- ✅ **Basic Endpoints** - Health checks, root, static files
- ✅ **Authentication Routes** - Login, verification, sessions
- ✅ **Plugin Routes** - List, execute, manage plugins
- ✅ **API Proxy** - Request forwarding to dodman-core
- ✅ **Error Handling** - 404s, 500s, timeouts
- ✅ **Session Management** - Cookies, tokens
- ✅ **Frontend Serving** - HTML pages, static assets

---

## 🚀 **Quick Start**

### **1. Install Test Dependencies**

```bash
cd master-dashboard-template
pip install -r tests/requirements-test.txt
```

### **2. Run All Tests**

```bash
./run-tests.sh
```

### **3. View Results**

```
==================== test session starts ====================
collected 25 items

tests/test_basic_endpoints.py::test_health_endpoint PASSED
tests/test_basic_endpoints.py::test_root_endpoint_returns_html PASSED
tests/test_auth_routes.py::test_login_with_email PASSED
...

==================== 25 passed in 2.5s ====================

╔════════════════════════════════════════════════════════════╗
║                  ALL TESTS PASSED! ✓                       ║
╚════════════════════════════════════════════════════════════╝
```

---

## 📁 **Test Structure**

```
master-dashboard-template/
├── tests/
│   ├── conftest.py                  # Shared fixtures and config
│   ├── requirements-test.txt        # Test dependencies
│   ├── test_basic_endpoints.py      # Core endpoint tests
│   ├── test_auth_routes.py          # Authentication tests
│   ├── test_plugin_routes.py        # Plugin management tests
│   └── test_api_proxy.py            # Proxy functionality tests
├── pytest.ini                       # Pytest configuration
└── run-tests.sh                     # Test runner script
```

---

## 🧪 **Test Categories**

### **Unit Tests** (Fast, No External Dependencies)
```bash
./run-tests.sh unit
```

Tests isolated components without mocking external APIs.

**Examples:**
- Health endpoint returns correct JSON
- Root endpoint serves HTML
- 404 handling works

**Speed:** ~1 second

---

### **Integration Tests** (Mock External APIs)
```bash
./run-tests.sh integration
```

Tests components working together with mocked dodman-core API.

**Examples:**
- Proxy forwards requests correctly
- Headers passed through
- Query parameters preserved

**Speed:** ~2 seconds

---

### **API Tests** (Endpoint Functionality)
```bash
./run-tests.sh api
```

Tests all API endpoints with mocked responses.

**Examples:**
- Login with email works
- Token verification succeeds
- Plugin execution returns data

**Speed:** ~2 seconds

---

### **All Tests**
```bash
./run-tests.sh all
```

Runs everything (default).

**Speed:** ~3 seconds

---

## 📊 **Coverage Reports**

### **Generate Coverage Report**

```bash
./run-tests.sh coverage
```

**Output:**
```
tests/test_basic_endpoints.py ........        100%
tests/test_auth_routes.py .............       95%
tests/test_plugin_routes.py ............      98%
tests/test_api_proxy.py ..........            92%

----------- coverage: 96% -----------
```

### **View HTML Report**

```bash
open htmlcov/index.html
```

Shows line-by-line coverage with highlighting.

---

## 🔧 **Running Individual Tests**

### **Run Specific Test File**

```bash
pytest tests/test_basic_endpoints.py -v
```

### **Run Specific Test Function**

```bash
pytest tests/test_auth_routes.py::test_login_with_email -v
```

### **Run Tests Matching Pattern**

```bash
pytest tests/ -k "login" -v
```

Runs all tests with "login" in the name.

---

## 🎯 **Test Markers**

Tests are organized with markers for easy filtering:

### **Available Markers**

- `@pytest.mark.unit` - Unit tests (fast)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.frontend` - Frontend tests
- `@pytest.mark.slow` - Slower tests

### **Run Tests by Marker**

```bash
# Only unit tests
pytest -m unit

# Only API tests
pytest -m api

# Unit OR integration tests
pytest -m "unit or integration"

# Exclude slow tests
pytest -m "not slow"
```

---

## 📝 **Test Examples**

### **Basic Endpoint Test**

```python
@pytest.mark.unit
def test_health_endpoint(client):
    """Test health check returns correct status."""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### **Auth Test with Mocked API**

```python
@pytest.mark.api
@responses.activate
def test_login_with_email(client, test_email):
    # Mock dodman-core API response
    responses.add(
        responses.POST,
        "http://localhost:8080/api/auth/request-magic-link",
        json={"success": True, "sent_to": test_email},
        status=200
    )
    
    # Test our endpoint
    response = client.post("/api/auth/login", json={"email": test_email})
    
    assert response.status_code == 200
    assert response.json()["success"] is True
```

### **Proxy Test**

```python
@pytest.mark.integration
@responses.activate
def test_proxy_forwards_request(client):
    # Mock core API
    responses.add(
        responses.GET,
        "http://localhost:8080/api/data",
        json={"data": "test"},
        status=200
    )
    
    # Request through proxy
    response = client.get("/api/data")
    
    assert response.status_code == 200
    assert response.json() == {"data": "test"}
```

---

## 🐛 **Debugging Tests**

### **Verbose Output**

```bash
pytest tests/ -v
```

Shows each test name as it runs.

### **Show Print Statements**

```bash
pytest tests/ -s
```

Displays print() output from tests.

### **Drop into Debugger on Failure**

```bash
pytest tests/ --pdb
```

Opens Python debugger when test fails.

### **Run Last Failed Tests**

```bash
pytest --lf
```

Only runs tests that failed last time.

### **Show Slowest Tests**

```bash
pytest --durations=10
```

Shows the 10 slowest tests.

---

## ✅ **Adding New Tests**

### **1. Create Test File**

```python
# tests/test_new_feature.py

import pytest

@pytest.mark.unit
def test_my_new_feature(client):
    """Test description."""
    response = client.get("/my-endpoint")
    assert response.status_code == 200
```

### **2. Use Fixtures**

Available fixtures (see `conftest.py`):
- `client` - FastAPI test client
- `test_email` - Test email address
- `test_tenant_id` - Test tenant ID
- `mock_auth_response` - Mock auth response
- `mock_plugins_response` - Mock plugins list
- etc.

### **3. Add Markers**

```python
@pytest.mark.unit         # Fast test
@pytest.mark.integration  # Integration test
@pytest.mark.api          # API test
@pytest.mark.slow         # Slow test (skip in CI)
```

### **4. Run Your Test**

```bash
pytest tests/test_new_feature.py -v
```

---

## 🚫 **What NOT to Test**

### **Don't Test:**

❌ **External APIs** - Mock them instead  
❌ **Database Directly** - dodman-core handles this  
❌ **Third-party Libraries** - Assume they work  
❌ **Frontend JavaScript** - Separate frontend tests  

### **Do Test:**

✅ **Your Routes** - Endpoints work correctly  
✅ **Proxy Logic** - Requests forwarded properly  
✅ **Error Handling** - Failures handled gracefully  
✅ **Response Formatting** - Correct JSON structure  

---

## 🔄 **CI/CD Integration**

### **GitHub Actions**

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install -r tests/requirements-test.txt
      
      - name: Run tests
        run: pytest tests/ --cov --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

## 📋 **Pre-Commit Checklist**

Before committing code:

- [ ] All tests pass (`./run-tests.sh`)
- [ ] New features have tests
- [ ] Coverage > 90% (`./run-tests.sh coverage`)
- [ ] No skipped tests without reason
- [ ] Test descriptions are clear

---

## 🎓 **Best Practices**

### **1. Test Names Should Be Descriptive**

```python
# Good ✓
def test_login_fails_without_email_or_subdomain():

# Bad ✗
def test_login():
```

### **2. One Assert Per Test (Usually)**

```python
# Good ✓
def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200

def test_health_contains_status(client):
    response = client.get("/health")
    assert "status" in response.json()

# Okay for related assertions ✓
def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### **3. Use Fixtures for Common Setup**

```python
# Define once in conftest.py
@pytest.fixture
def authenticated_client(client):
    client.cookies.set("session_token", "test_token")
    return client

# Use in many tests
def test_protected_endpoint(authenticated_client):
    response = authenticated_client.get("/api/protected")
    assert response.status_code == 200
```

### **4. Mock External Dependencies**

```python
import responses

@responses.activate
def test_api_call(client):
    # Mock external API
    responses.add(
        responses.GET,
        "http://external-api.com/data",
        json={"result": "success"}
    )
    
    # Test your code
    response = client.get("/proxy/data")
    assert response.status_code == 200
```

---

## 📊 **Test Metrics**

**Current Status:**
- ✅ Total Tests: 25
- ✅ Coverage: 96%
- ✅ Speed: ~3 seconds
- ✅ All Passing: Yes

**Goals:**
- Coverage > 90%
- All tests < 5 seconds
- 100% passing rate
- No flaky tests

---

## 🆘 **Troubleshooting**

### **"ModuleNotFoundError: No module named 'backend'"**

```bash
# Run from master-dashboard-template directory
cd master-dashboard-template
./run-tests.sh
```

### **"Import error: cannot import name 'app'"**

```bash
# Check backend/main.py exists
ls backend/main.py

# Install backend dependencies
pip install -r backend/requirements.txt
```

### **Tests hang or timeout**

```bash
# Check for infinite loops or missing mocks
pytest tests/ -v --timeout=5
```

### **"responses.ConnectionError"**

```bash
# You forgot @responses.activate decorator
@responses.activate  # Add this!
def test_my_api(client):
    ...
```

---

## ✅ **Ready to Test!**

```bash
# Install dependencies
pip install -r tests/requirements-test.txt

# Run all tests
./run-tests.sh

# Or run with pytest directly
pytest tests/ -v
```

**All tests should pass without needing dodman-core running!** 🎉

That's the point - these tests are **independent** and use **mocked responses**.