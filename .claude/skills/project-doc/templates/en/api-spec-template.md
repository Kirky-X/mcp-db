# API Specification Document

> **Project Name**: [Project Name]  
> **API Version**: v1.0.0  
> **Creation Date**: YYYY-MM-DD  
> **Last Updated**: YYYY-MM-DD  
> **Maintainer**: [Maintainer Name]

---

## 📋 Document Description

This document defines the RESTful API specification for the project, including:
- General specifications and conventions
- Authentication and authorization mechanisms
- Detailed interface definitions
- Data models
- Error code definitions

**Target Audience**: Frontend developers, backend developers, QA engineers, third-party integration developers

---

## 🌐 API Basic Information

### Base URL

| Environment | URL | Description |
|------|-----|------|
| Development | `https://dev-api.example.com` | For local development and debugging |
| Testing | `https://test-api.example.com` | For testing and QA |
| Staging | `https://staging-api.example.com` | Final verification before production |
| Production | `https://api.example.com` | Official public service |

### Version Control

API versioning is controlled via URL path:
```
https://api.example.com/v1/users
https://api.example.com/v2/users
```

### Supported Protocols

- **HTTPS** (Mandatory): All production APIs must use HTTPS
- **HTTP** (Development Only): Development environment may use HTTP

---

## 🔐 Authentication & Authorization

### Authentication Method

This API uses **JWT (JSON Web Token)** for identity authentication.

#### Obtain Token

**Request Example**:
```http
POST /v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "securePassword123"
}
```

**Response Example**:
```json
{
  "code": 0,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

#### Use Token

In all requests requiring authentication, add the `Authorization` header:

```http
GET /v1/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Refresh Token

After the Access Token expires, use the Refresh Token to obtain a new Access Token:

```http
POST /v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Access Control

The API uses Role-Based Access Control (RBAC):

| Role | Permission Description |
|------|----------|
| `admin` | System administrator, has all permissions |
| `manager` | Business administrator, has business-related management permissions |
| `user` | Regular user, has basic read and write permissions |
| `guest` | Visitor, has read-only permissions |

Insufficient permissions return `403 Forbidden`.

---

## 📡 General Specifications

### HTTP Methods

| Method | Usage | Idempotency |
|------|------|--------|
| `GET` | Retrieve resource | Yes |
| `POST` | Create resource | No |
| `PUT` | Fully update resource (replace entire resource) | Yes |
| `PATCH` | Partially update resource (update specific fields) | No |
| `DELETE` | Delete resource | Yes |

### Status Codes

| Status Code | Meaning | Usage Scenario |
|--------|------|----------|
| `200 OK` | Request successful | Success for GET, PUT, PATCH, DELETE |
| `201 Created` | Resource created successfully | Success for POST creating a resource |
| `204 No Content` | Request successful but no content returned | Optional for DELETE success |
| `400 Bad Request` | Request parameter error | Parameter validation failed |
| `401 Unauthorized` | Not authenticated | Missing or invalid Token |
| `403 Forbidden` | Insufficient permissions | User lacks authority to access the resource |
| `404 Not Found` | Resource does not exist | Requested resource was not found |
| `409 Conflict` | Resource conflict | Uniqueness constraint conflict (e.g., duplicate username) |
| `422 Unprocessable Entity` | Business logic error | Business rule validation failed |
| `429 Too Many Requests` | Too frequent requests | Rate limit triggered |
| `500 Internal Server Error` | Server error | Internal server exception |
| `503 Service Unavailable` | Service unavailable | Service under maintenance or overloaded |

### Request Headers

#### Required Headers

```http
Content-Type: application/json
Accept: application/json
```

#### Recommended Headers

```http
User-Agent: MyApp/1.0.0 (iOS; iPhone; 15.0)
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
X-Request-ID: uuid-v4-string
```

### Response Format

All API responses use a unified JSON format:

#### Success Response

```json
{
  "code": 0,
  "message": "Operation successful",
  "data": {
    "id": 123,
    "name": "Example Data"
  }
}
```

#### Error Response

```json
{
  "code": 40001,
  "message": "Invalid username or password",
  "errors": [
    {
      "field": "password",
      "message": "Password length cannot be less than 8 characters"
    }
  ],
  "request_id": "uuid-v4-string",
  "timestamp": 1640000000
}
```

#### Field Description

| Field | Type | Required | Description |
|------|------|------|------|
| `code` | integer | Yes | Business status code, 0 indicates success |
| `message` | string | Yes | Status message |
| `data` | object/array | No | Response data, present on success |
| `errors` | array | No | Error details, present on failure |
| `request_id` | string | No | Request tracking ID |
| `timestamp` | integer | No | Response timestamp (Unix time) |

---

## 🗂️ Data Model

### User

```json
{
  "id": 123,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "avatar": "https://cdn.example.com/avatar/123.jpg",
  "role": "user",
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-02T00:00:00Z"
}
```

| Field | Type | Description |
|------|------|------|
| `id` | integer | Unique user identifier |
| `username` | string | Username, 3-20 characters |
| `email` | string | Email address |
| `full_name` | string | Real name |
| `avatar` | string | Avatar URL |
| `role` | string | Role: `admin` / `manager` / `user` / `guest` |
| `status` | string | Status: `active` / `inactive` / `suspended` |
| `created_at` | string | Creation time (ISO 8601) |
| `updated_at` | string | Update time (ISO 8601) |

---
**End of Document**
