# Code Review Report

**Repository:** Customer
**Reviewed scope:** All source files
**Generated at (UTC):** 2026-10-11 10:42:18

## Executive Summary

The repository contains several critical issues: hard‑coded database credentials, a guaranteed NullReferenceException in a service class, and missing authorization on API endpoints. These affect security, reliability, and overall code quality.

## Findings Summary

- **Total findings:** 4
- **Critical:** 0
- **High:** 2
- **Medium:** 1
- **Low:** 1
- **Info:** 0

## Detailed Findings

### 1. [High] Hard‑coded database credentials

- **Category:** Security
- **Location:** `Customer.Infrastructure/CustomerRepository.cs:9-10`
- **Confidence:** 96%

**Description**

The repository stores a full SQL Server connection string with the SA user and a plain‑text password directly in source code. This exposes privileged credentials and makes the application vulnerable to credential leakage and unauthorized database access.

**Evidence**

> var connectionString = "Server=localhost;Database=CustomerDb;User Id=sa;Password=Password123;";

**Recommendation**

Move the connection string to a secure configuration source (e.g., environment variables, Azure Key Vault, user‑secrets) and never commit plain passwords. Use integrated security or a limited‑privilege account for the application.

---

### 2. [High] Guaranteed NullReferenceException in CustomerService

- **Category:** Reliability
- **Location:** `Customer.Api/Services/CustomerService.cs:5-7`
- **Confidence:** 94%

**Description**

CustomerService.GetCustomerName initializes `customerName` to null and immediately calls `customerName.ToUpper()`. This will always throw a NullReferenceException, causing the API to fail whenever the method is invoked.

**Evidence**

> string customerName = null;
> 
> return customerName.ToUpper();

**Recommendation**

Validate that `customerName` is not null before calling methods on it, or return a default value / throw a meaningful exception. Example: `return (customerName ?? string.Empty).ToUpper();`

---

### 3. [Medium] API endpoints lack authorization attributes

- **Category:** Security
- **Location:** `Customer.Api/Controllers/CustomerController.cs:1-32`
- **Confidence:** 88%

**Description**

The controller `CustomerController` does not apply any `[Authorize]` attribute, while the application pipeline enables authentication and authorization middleware. Consequently, all endpoints are publicly accessible, exposing potentially sensitive operations.

**Evidence**

> [ApiController]
> [Route("api/customers")]
> public class CustomerController : ControllerBase
> { ... }

**Recommendation**

Add appropriate `[Authorize]` attributes (or policy‑based authorization) to protect the endpoints, and configure authentication schemes as needed.

---

### 4. [Low] Unreachable NotFound branch in GetCustomer endpoint

- **Category:** Code Quality
- **Location:** `Customer.Api/Controllers/CustomerController.cs:9-15`
- **Confidence:** 80%

**Description**

The `GetCustomer` action returns `NotFound()` only when `customerName.Length <= 5`. Since `customerName` is always built as "Customer-" + id, its length is at least 10, making the `NotFound` branch unreachable and indicating a logic error.

**Evidence**

> var customerName = "Customer-" + id;
> 
> if (customerName.Length > 5)
> {
>     return Ok(customerName);
> }
> 
> return NotFound();

**Recommendation**

Review the intended business rule and adjust the condition or response accordingly. If a NotFound should be returned for missing records, integrate a data lookup instead of a static string.

---

## Review Limitations

This report reflects the files and evidence available to the agent. Findings require developer verification; absence of findings does not prove the code is secure.
