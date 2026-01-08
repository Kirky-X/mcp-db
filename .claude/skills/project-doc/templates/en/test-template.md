# Test Document

> **Document Version**: v1.0  
> **Creation Date**: YYYY-MM-DD  
> **Last Updated**: YYYY-MM-DD  
> **Document Status**: ⏳ Draft / 📝 In Review / ✅ Approved  
> **Test Lead**: [Name]  
> **Reviewers**: [List of Names]

---

## 📋 Document Revision History

| Version | Date | Revised By | Revision Description |
|------|------|--------|----------|
| v1.0 | YYYY-MM-DD | [Name] | Initial Version |
| v1.1 | YYYY-MM-DD | [Name] | [Revision Description] |

---

## 1. Test Overview

### 1.1 Test Goals

**Quality Goals**:
- Ensure the product meets all functional requirements defined in the PRD
- Verify the system satisfies non-functional requirements defined in the TDD
- Guarantee code quality and system stability
- Reduce production defect rate to < 0.1%

**Test Scope**:
- ✅ Functional Testing
- ✅ Interface (API) Testing
- ✅ Performance Testing
- ✅ Security Testing
- ✅ Compatibility Testing
- ⚠️ Usability Testing (Simplified)
- ❌ Stress Testing (Not executed in MVP stage)

### 1.2 Test Strategy

**Test Pyramid**:

```
           /\
          /  \      E2E Testing (10%)
         /____\     
        /      \    Integration Testing (30%)
       /________\   
      /          \  Unit Testing (60%)
     /____________\ 
```

**Test Type Distribution**:
- **Unit Testing**: 60% - Fast feedback, covering core logic
- **Integration Testing**: 30% - Verifying interaction between modules
- **End-to-End Testing**: 10% - Verifying critical user flows

### 1.3 Test Environment

| Environment | Purpose | Data | Access URL |
|------|------|------|---------|
| Development (Dev) | Developer self-test | Mock Data | http://dev.example.com |
| Testing (Test) | Functional/Integration Testing | Test Data | http://test.example.com |
| Staging | UAT, Performance Testing | Production-mirrored Data | http://staging.example.com |
| Production (Prod) | Real user access | Production Data | https://www.example.com |

### 1.4 Test Tools

| Test Type | Tool | Version | Purpose |
|---------|------|------|------|
| Unit Testing | pytest | 7.4+ | Python Unit Testing |
| Unit Testing | Jest | 29+ | JavaScript Unit Testing |
| Integration Testing | pytest + TestClient | - | API Integration Testing |
| E2E Testing | Playwright | 1.40+ | End-to-End Automated Testing |
| Performance Testing | Locust | 2.17+ | Load and Stress Testing |
| API Testing | Postman / Newman | - | API Manual/Automated Testing |
| Security Scanning | Bandit / SonarQube | - | Code Security Scanning |
| Coverage | pytest-cov | - | Code Coverage Statistics |

### 1.5 Test Metrics

**Quality Metrics**:

| Metric | Target Value | Measurement |
|------|--------|---------|
| Unit Test Coverage | > 80% | pytest-cov |
| Integration Test Pass Rate | 100% | CI/CD Report |
| E2E Test Pass Rate | 100% | Playwright Report |
| Defect Density | < 5 per KLOC | Defect Management System |
| Defect Fix Rate | > 95% (Before Release) | Defect Management System |
| Average Defect Fix Time | < 2 Days | Defect Management System |

---

## 2. Test Plan

### 2.1 Test Phases

| Phase | Duration | Test Type | Owner | Exit Criteria |
|------|------|---------|--------|---------|
| Development | YYYY-MM-DD ~ YYYY-MM-DD | Unit Testing | Developers | Coverage > 80% |
| Functional Testing | YYYY-MM-DD ~ YYYY-MM-DD | Functional/Integration Testing | QA Team | All P0/P1 functions passed |
| System Testing | YYYY-MM-DD ~ YYYY-MM-DD | Performance/Security Testing | QA Team | Performance metrics met |
| Acceptance Testing | YYYY-MM-DD ~ YYYY-MM-DD | UAT | PM + Key Users | Acceptance criteria passed |

### 2.2 Test Milestones

- **Unit Testing Completed**: YYYY-MM-DD
- **Integration Testing Completed**: YYYY-MM-DD
- **Functional Testing Completed**: YYYY-MM-DD
- **Performance Testing Completed**: YYYY-MM-DD
- **Regression Testing Completed**: YYYY-MM-DD
- **Ready for Release**: YYYY-MM-DD

### 2.3 Resource Allocation

**Personnel**:
- QA Engineers: 3
- Automation Test Engineer: 1
- Performance Test Engineer: 1 (Part-time)

**Hardware Resources**:
- Test Servers: 2 (4 Core 8GB)
- Performance Test Env: Same as Production configuration

---

## 3. Unit Testing

### 3.1 Unit Testing Strategy

**Testing Principles**:
- Independence: Each test case runs independently
- Repeatability: Consistent results across multiple runs
- Fast Execution: Individual test < 100ms
- Clear Assertions: Each test verifies one behavior

**Test Coverage**:
- Critical Business Logic: 100% Coverage
- Utility Functions: 100% Coverage
- Data Models: 80% Coverage
- API Routes: 80% Coverage

### 3.2 Unit Test Cases

#### 3.2.1 User Authentication Module

**Module**: `auth.service.AuthService`  
**Status**: ⏳ Pending
**Test Case: User Registration**

| Case ID | Test Scenario | Input | Expected Output | Priority | Status |
|---------|---------|------|---------|--------|------|
| UT-AUTH-001 | Normal Registration | Valid email, password | Returns User object, password encrypted | P0 | ⏳ Pending |
| UT-AUTH-002 | Email Already Exists | Registered email | Raises `EmailAlreadyExists` exception | P0 | ⏳ Pending |
| UT-AUTH-003 | Invalid Email Format | Invalid email format | Raises `ValidationError` exception | P1 | ⏳ Pending |
| UT-AUTH-004 | Password Too Short | Password < 8 chars | Raises `ValidationError` exception | P1 | ⏳ Pending |
| UT-AUTH-005 | Password Strength Weak | Numeric-only password | Raises `ValidationError` exception | P1 | ⏳ Pending |

**Example Code**:

```python
import pytest
from app.services.auth import AuthService
from app.exceptions import EmailAlreadyExists, ValidationError

class TestAuthService:
    @pytest.fixture
    def auth_service(self, db_session):
        return AuthService(db_session)
    
    def test_register_success(self, auth_service):
        """UT-AUTH-001: Normal Registration"""
        user = auth_service.register(
            email="test@example.com",
            password="SecurePass123",
            username="testuser"
        )
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.password_hash != "SecurePass123"  # Password encrypted
        assert len(user.password_hash) > 0
    
    def test_register_duplicate_email(self, auth_service):
        """UT-AUTH-002: Email Already Exists"""
        auth_service.register(
            email="test@example.com",
            password="SecurePass123",
            username="testuser1"
        )
        
        with pytest.raises(EmailAlreadyExists):
            auth_service.register(
                email="test@example.com",
                password="AnotherPass123",
                username="testuser2"
            )
    
    def test_register_invalid_email(self, auth_service):
        """UT-AUTH-003: Invalid Email Format"""
        with pytest.raises(ValidationError):
            auth_service.register(
                email="invalid-email",
                password="SecurePass123",
                username="testuser"
            )
```

**Test Case: User Login**

| Case ID | Test Scenario | Input | Expected Output | Priority | Status |
|---------|---------|------|---------|--------|------|
| UT-AUTH-011 | Normal Login | Correct email and password | Returns Access Token and Refresh Token | P0 | ⏳ Pending |
| UT-AUTH-012 | Wrong Password | Correct email, wrong password | Raises `InvalidCredentials` exception | P0 | ⏳ Pending |
| UT-AUTH-013 | User Not Found | Unregistered email | Raises `UserNotFound` exception | P0 | ⏳ Pending |
| UT-AUTH-014 | Account Locked | Locked account | Raises `AccountLocked` exception | P1 | ⏳ Pending |
| UT-AUTH-015 | Login Fail Limit | 5 consecutive wrong passwords | Account locked for 15 minutes | P1 | ⏳ Pending |

**Test Case: Token Verification**

| Case ID | Test Scenario | Input | Expected Output | Priority | Status |
|---------|---------|------|---------|--------|------|
| UT-AUTH-021 | Valid Token | Valid JWT Token | Returns User Info | P0 | ⏳ Pending |
| UT-AUTH-022 | Token Expired | Expired Token | Raises `TokenExpired` exception | P0 | ⏳ Pending |
| UT-AUTH-023 | Invalid Token Format | Malformed Token | Raises `InvalidToken` exception | P0 | ⏳ Pending |
| UT-AUTH-024 | Token Revoked | Logged-out Token | Raises `TokenRevoked` exception | P1 | ⏳ Pending |

---

#### 3.2.2 [Other Module]

**Module**: `[Module Path]`  
**Status**: ⏳ Pending

(Continue adding unit test cases for other modules following the structure above)

---

### 3.3 Unit Test Coverage Requirements

| Module | Min Coverage | Current Coverage | Status |
|------|-----------|-----------|------|
| Auth Module | 90% | - % | ⏳ Pending |
| User Management | 80% | - % | ⏳ Pending |
| Content Management | 80% | - % | ⏳ Pending |
| Utility Functions | 100% | - % | ⏳ Pending |
| Overall | 80% | - % | ⏳ Pending |

---

## 4. Integration Testing

### 4.1 Integration Testing Strategy

**Test Scope**:
- API Interface Testing
- Database Operation Testing
- Inter-service Interaction Testing
- Third-party Service Integration Testing (Mock)

**Test Environment**:
- Use Test Database
- Mock External Services (Email, SMS, Payment)
- Use TestClient to simulate HTTP requests

### 4.2 API Integration Test Cases

#### 4.2.1 User Registration API

**Endpoint**: `POST /api/v1/auth/register`  
**Status**: ⏳ Pending

| Case ID | Test Scenario | Request Data | Expected Response | HTTP Status | Priority | Status |
|---------|---------|---------|---------|-----------|--------|------|
| IT-REG-001 | Normal Registration | `{"email": "test@example.com", "password": "Pass123", "username": "test"}` | Returns User Info and Token | 201 | P0 | ⏳ Pending |
| IT-REG-002 | Email Already Exists | Registered email | `{"code": 409001, "message": "Email already exists"}` | 409 | P0 | ⏳ Pending |
| IT-REG-003 | Missing Required Field | `{"email": "test@example.com"}` | `{"code": 400001, "message": "Missing required field: password"}` | 400 | P1 | ⏳ Pending |
| IT-REG-004 | Invalid Email Format | `{"email": "invalid", "password": "Pass123"}` | `{"code": 400001, "message": "Invalid email format"}` | 400 | P1 | ⏳ Pending |
| IT-REG-005 | Duplicate Username | Existing username | `{"code": 409002, "message": "Username already exists"}` | 409 | P1 | ⏳ Pending |

**Example Code**:

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

class TestUserRegistration:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_register_success(self, client):
        """IT-REG-001: Normal Registration"""
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "SecurePass123",
            "username": "testuser"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["code"] == 0
        assert "data" in data
        assert "access_token" in data["data"]
        assert data["data"]["user"]["email"] == "test@example.com"
    
    def test_register_duplicate_email(self, client):
        """IT-REG-002: Email Already Exists"""
        # Register once
        client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "Pass123",
            "username": "user1"
        })
        
        # Try duplicate registration
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "Pass456",
            "username": "user2"
        })
        
        assert response.status_code == 409
        data = response.json()
        assert data["code"] == 409001
        assert "already exists" in data["message"].lower()
```

---

#### 4.2.2 User Login API

**Endpoint**: `POST /api/v1/auth/login`  
**Status**: ⏳ Pending

| Case ID | Test Scenario | Request Data | Expected Response | HTTP Status | Priority | Status |
|---------|---------|---------|---------|-----------|--------|------|
| IT-LOGIN-001 | Normal Login | Correct email and password | Returns Token | 200 | P0 | ⏳ Pending |
| IT-LOGIN-002 | Wrong Password | Wrong password | `{"code": 401001, "message": "Invalid credentials"}` | 401 | P0 | ⏳ Pending |
| IT-LOGIN-003 | User Not Found | Unregistered email | `{"code": 404001, "message": "User not found"}` | 404 | P0 | ⏳ Pending |
| IT-LOGIN-004 | Account Locked | Locked account | `{"code": 403002, "message": "Account locked"}` | 403 | P1 | ⏳ Pending |

---

#### 4.2.3 [Other APIs]

(Continue adding integration test cases for other APIs)

---

### 4.3 Database Integration Testing

#### 4.3.1 Transaction Consistency Testing

| Case ID | Test Scenario | Steps | Expected Result | Priority | Status |
|---------|---------|---------|---------|--------|------|
| IT-DB-001 | Transaction Rollback | 1. Start Transaction<br>2. Insert Data<br>3. Simulate Exception<br>4. Rollback | Data not written to DB | P0 | ⏳ Pending |
| IT-DB-002 | Concurrent Write | Multiple threads writing to same record | Data consistent, no dirty/phantom reads | P1 | ⏳ Pending |
| IT-DB-003 | Foreign Key Constraint | Insert data referencing non-existent FK | Raises Foreign Key error | P1 | ⏳ Pending |

---

### 4.4 Third-party Service Integration Testing (Mock)

#### 4.4.1 Email Service

| Case ID | Test Scenario | Mock Config | Verification Point | Priority | Status |
|---------|---------|----------|--------|--------|------|
| IT-EMAIL-001 | Send Verification Email | Mock SendGrid API | Correct params, content includes link | P1 | ⏳ Pending |
| IT-EMAIL-002 | Email Send Failed | Mock returns 500 | Error logged, entered retry queue | P2 | ⏳ Pending |

#### 4.4.2 SMS Service

| Case ID | Test Scenario | Mock Config | Verification Point | Priority | Status |
|---------|---------|----------|--------|--------|------|
| IT-SMS-001 | Send OTP | Mock SMS API | OTP is 6 digits, valid for 5 mins | P1 | ⏳ Pending |
| IT-SMS-002 | SMS Rate Limit | Multiple requests in 1 min | Second request rejected | P1 | ⏳ Pending |

---

## 5. End-to-End Testing (E2E)

### 5.1 E2E Testing Strategy

**Test Scope**:
- Critical User Flows
- Cross-page Interaction
- Full Frontend-Backend Integration

**Test Tool**: Playwright

**Test Environment**: Staging

### 5.2 E2E Test Cases

#### 5.2.1 User Registration Flow

**Scenario ID**: E2E-001  
**Priority**: P0  
**Status**: ⏳ Pending

**Pre-conditions**:
- Access registration page
- Email not previously registered

**Test Steps**:

| Step | Action | Expected Result |
|------|------|---------|
| 1 | Visit `/register` | Registration form displayed |
| 2 | Enter email: `test@example.com` | Email field filled |
| 3 | Enter password: `SecurePass123` | Password field filled, shown as `***` |
| 4 | Enter username: `testuser` | Username field filled |
| 5 | Click "Register" button | Loading state shown |
| 6 | Wait for response | Redirected to Home, welcome message shown |
| 7 | Verify localStorage | `access_token` exists |
| 8 | Verify top nav | Username and logout button shown |

**Example Code**:

```javascript
// e2e/auth/register.spec.js
import { test, expect } from '@playwright/test';

test.describe('User Registration', () => {
  test('should register successfully', async ({ page }) => {
    // E2E-001: User Registration Flow
    await page.goto('/register');
    
    // Fill form
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'SecurePass123');
    await page.fill('input[name="username"]', 'testuser');
    
    // Click register
    await page.click('button[type="submit"]');
    
    // Wait for navigation to home
    await page.waitForURL('/');
    
    // Verify user logged in
    await expect(page.locator('.username')).toContainText('testuser');
    
    // Verify token stored
    const token = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(token).toBeTruthy();
  });
});
```

---

#### 5.2.2 User Login → Publish Content → Logout Flow

**Scenario ID**: E2E-002  
**Priority**: P0  
**Status**: ⏳ Pending

**Test Steps**:

| Step | Action | Expected Result |
|------|------|---------|
| 1 | Visit Login page `/login` | Login form displayed |
| 2 | Enter registered email/password | Form filled |
| 3 | Click "Login" | Redirected to Home |
| 4 | Click "Publish" button | Publish form displayed |
| 5 | Fill Title and Content | Form filled |
| 6 | Click "Submit" | Success toast, redirected to Detail page |
| 7 | Verify Content Published | Detail page shows the new content |
| 8 | Click "Logout" | Redirected to Login, localStorage cleared |

---

#### 5.2.3 [Other Critical Flows]

(Continue adding other critical user flow E2E cases)

---

## 6. Performance Testing

### 6.1 Performance Goals

| Metric | Target Value | Test Method |
|------|--------|---------|
| Response Time (P50) | < 100ms | Locust Load Test |
| Response Time (P95) | < 200ms | Locust Load Test |
| Response Time (P99) | < 500ms | Locust Load Test |
| Concurrent Users | 10,000+ | Locust Concurrency Test |
| QPS | 10,000+ | Locust Stress Test |
| Error Rate | < 0.1% | Locust Monitoring |

### 6.2 Performance Scenarios

#### 6.2.1 Login API Performance Test

**Scenario ID**: PERF-001  
**Status**: ⏳ Pending

**Configuration**:
- Concurrent Users: 1000
- Duration: 10 minutes
- Spawn Rate: 100 users/sec

**Steps**:
1. Simulate 1000 users logging in concurrently
2. Record response times and success rates
3. Monitor server resource usage

**Pass Criteria**:
- P95 Response Time < 200ms
- Success Rate > 99.9%
- CPU Usage < 80%
- Memory Usage < 80%

**Example Code**:

```python
# locustfile.py
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def login(self):
        """PERF-001: Login Performance Test"""
        self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "SecurePass123"
        })
```

---

#### 6.2.2 Article List Query Performance Test

**Scenario ID**: PERF-002  
**Status**: ⏳ Pending

**Configuration**:
- Concurrent Users: 5000
- Duration: 15 minutes
- Data Volume: 1 Million Articles

**Steps**:
1. Pre-load 1 million articles
2. Simulate 5000 concurrent users querying article list
3. Test pagination performance (Page 1, 100, 10000)

**Pass Criteria**:
- Page 1 Response < 50ms
- Page 100 Response < 100ms
- Page 10000 Response < 200ms
- DB Query Time < 50ms

---

#### 6.2.3 Concurrent Write Performance Test

**Scenario ID**: PERF-003  
**Status**: ⏳ Pending

**Configuration**:
- Concurrent Users: 500
- 10 articles per user
- Total 5000 articles

**Steps**:
1. 500 users publish content simultaneously
2. Monitor DB write performance
3. Check data consistency

**Pass Criteria**:
- Success Rate > 99%
- No data loss
- No concurrency conflict errors

---

### 6.3 Stress Testing

**Goal**: Identify system bottlenecks and maximum capacity.

**Scenario**:
- Gradually increase concurrent users (1000 → 5000 → 10000 → 20000)
- Observe when performance degrades or errors occur

**Metrics to Record**:
- Max supported concurrency
- Performance knee point (where response time spikes)
- System breaking point

---

## 7. Security Testing

### 7.1 Security Scope

- ✅ SQL Injection Testing
- ✅ XSS Attack Testing
- ✅ CSRF Attack Testing
- ✅ Auth Bypass Testing
- ✅ Privilege Escalation Testing
- ✅ Sensitive Info Leakage Testing
- ✅ Dependency Vulnerability Scanning

### 7.2 Security Test Cases

#### 7.2.1 SQL Injection Testing

**Scenario ID**: SEC-001  
**Status**: ⏳ Pending

| Case | Injection Point | Payload | Expected Result |
|------|--------|---------|---------|
| SEC-001-01 | Login Email Field | `' OR '1'='1` | Login fails, 400 error |
| SEC-001-02 | Search Keywords | `'; DROP TABLE users; --` | Search fails, SQL not executed |
| SEC-001-03 | User ID Param | `1 OR 1=1` | Param validation fails |

**Verification Methods**:
- Auto-scan with SQLMap
- Manual injection attempts
- Check logs for abnormal SQL records

---

#### 7.2.2 XSS Attack Testing

**Scenario ID**: SEC-002  
**Status**: ⏳ Pending

| Case | Injection Point | Payload | Expected Result |
|------|--------|---------|---------|
| SEC-002-01 | Article Content | `<script>alert('XSS')</script>` | Content escaped, script not executed |
| SEC-002-02 | Username | `<img src=x onerror=alert('XSS')>` | Username escaped |
| SEC-002-03 | Comment Content | `<a href="javascript:alert('XSS')">Link</a>` | JS protocol filtered |

---

#### 7.2.3 Auth and Privilege Testing

**Scenario ID**: SEC-003  
**Status**: ⏳ Pending
