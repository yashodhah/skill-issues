---
name: api-conventions
description: Use when writing or reviewing REST controllers, HTTP endpoints, URL paths, route naming, HTTP verbs, status codes in a Spring Boot project
---

# API Conventions — REST

Three rules covering HTTP verbs, URL structure, and status codes.

All three are feedforward rules — AI code review references their IDs in PR comments.

## Rules

### API-001 — Use correct HTTP verbs

Match the verb to the intent. Never use GET for mutations.

| Verb | Use for |
|------|---------|
| `GET` | Read — must be safe and idempotent, no side effects |
| `POST` | Create a new resource |
| `PUT` | Full replace of an existing resource |
| `PATCH` | Partial update of an existing resource |
| `DELETE` | Remove a resource |

```java
// ❌ API-001 violation
@GetMapping("/users/{id}/deactivate")  // GET with side effect

// ✅ correct
@PostMapping("/users/{id}/deactivation")  // or DELETE /users/{id}/activation
```

---

### API-002 — No verbs in URL paths

URLs identify resources (nouns), not actions (verbs). Use plural nouns.

```
// ❌ API-002 violations
GET  /getUser/42
POST /createOrder
GET  /users/42/doDeactivate

// ✅ correct
GET    /users/42
POST   /orders
DELETE /users/42/activation
```

Sub-resources are fine: `/users/{id}/orders` reads as "orders belonging to user".

---

### API-003 — Return correct HTTP status codes

```java
// ❌ returning 200 for everything
return ResponseEntity.ok(createdUser);          // should be 201
return ResponseEntity.ok().build();             // empty body should be 204

// ✅ correct
return ResponseEntity
    .created(URI.create("/users/" + user.getId()))
    .body(user);                                // 201 Created with Location header

return ResponseEntity.noContent().build();      // 204 No Content

// In @ExceptionHandler / @RestControllerAdvice:
// 400 Bad Request   — validation failures (@Valid, @Validated)
// 404 Not Found     — resource does not exist
// 409 Conflict      — duplicate, version mismatch
// 500               — unhandled — never return this intentionally
```

**Rule of thumb:** if the response body is empty, use 204. If a resource was just created, use 201 with a `Location` header.

---

## Quick reference

| ID | Rule | Enforced by |
|----|------|-------------|
| `API-001` | Correct HTTP verb for the intent | AI code review (PR) |
| `API-002` | No verbs in URL paths, plural nouns | AI code review (PR) |
| `API-003` | Correct status codes (201/204/400/404/409) | AI code review (PR) |
