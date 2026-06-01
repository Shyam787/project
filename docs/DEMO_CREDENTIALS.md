# Demo Credentials

## Organization Information

Organization Name: ACME Corporation

Organization ID: acme

This organization is seed data for evaluator demonstrations only. Production flows do not depend on ACME-specific logic.

## User Accounts

| Email | Role | Password |
| --- | --- | --- |
| admin@acme.com | tenant_admin | DemoAdmin123! |
| manager@acme.com | manager | DemoManager123! |
| employee@acme.com | employee | DemoEmployee123! |
| viewer@acme.com | viewer | DemoViewer123! |

| admin@abcd.com | tenant_admin | DemoAdmin123! |

## Login Instructions

1. Open http://localhost:3002/login.
2. Sign in with email and password.
3. Tenant context is resolved from Keycloak token claims.
4. Administrators can create additional users from Users.
