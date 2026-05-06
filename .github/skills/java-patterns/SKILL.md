---
name: java-patterns
description: Use when writing, reviewing, or asking about Java code in a Spring Boot project — error handling, exceptions, catch blocks, constructor injection, @Autowired on fields, service methods, null returns, Optional
---

# Java Patterns — Spring Boot

Three rules. One per pillar: error handling, Spring structure, code clarity.

## Rules

### JAVA-001 — Catch specific exceptions, never bare `Exception`

Never catch `Exception`, `Throwable`, or `RuntimeException`. Always catch the narrowest type.

```java
// ❌ JAVA-001 violation — Checkstyle will flag this
try {
    userService.find(id);
} catch (Exception e) {
    log.error("failed", e);
}

// ✅ correct
try {
    userService.find(id);
} catch (UserNotFoundException e) {
    log.warn("user {} not found", id);
} catch (DataAccessException e) {
    log.error("db error looking up user {}", id, e);
}
```

**Linter:** Checkstyle `IllegalCatch` fires `JAVA-001` on commit.

---

### JAVA-002 — Constructor injection, never `@Autowired` on fields

Field injection hides dependencies and breaks testability. Spring auto-wires single-constructor beans — no annotation needed.

```java
// ❌ JAVA-002 violation — ArchUnit will catch this
@RestController
public class UserController {
    @Autowired
    private UserService userService;
}

// ✅ correct
@RestController
public class UserController {
    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }
}
```

**Linter:** ArchUnit test `JAVA-002` fails if any Spring bean has an `@Autowired` field.

---

### JAVA-003 — Service methods must not return `null`

Return `Optional<T>` for values that may be absent. Throw a specific exception for error cases. `null` is invisible at the call site and causes NPEs far from the source.

```java
// ❌ JAVA-003 violation — AI review will flag this
public User findUser(Long id) {
    return repository.findById(id).orElse(null);
}

// ✅ correct — absent value
public Optional<User> findUser(Long id) {
    return repository.findById(id);
}

// ✅ correct — expected presence (not-found is exceptional)
public User getUser(Long id) {
    return repository.findById(id)
        .orElseThrow(() -> new UserNotFoundException(id));
}
```

**Enforcement:** Feedforward only. AI code review references `JAVA-003` in PR comments.

---

## Quick reference

| ID | Rule | Enforced by |
|----|------|-------------|
| `JAVA-001` | No bare `Exception` catch | Checkstyle (`mvn verify`) |
| `JAVA-002` | No `@Autowired` fields | ArchUnit (`mvn test`) |
| `JAVA-003` | No `null` returns from services | AI code review (PR) |
