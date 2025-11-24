// Comprehensive Java test file with complex structures
package com.chromium.test.complex;

import java.util.*;
import java.io.*;

/**
 * Base interface for authentication
 */
public interface Authenticator {
    boolean authenticate(String username, String password);

    void logout();
}

/**
 * Abstract base class for users
 */
public abstract class User {
    protected String username;
    protected int id;

    public User(String username, int id) {
        this.username = username;
        this.id = id;
    }

    public abstract String getRole();
}

/**
 * Admin user with elevated privileges
 */
public class AdminUser extends User implements Authenticator {
    private List<String> permissions;

    public AdminUser(String username, int id) {
        super(username, id);
        this.permissions = new ArrayList<>();
    }

    @Override
    public String getRole() {
        return "ADMIN";
    }

    @Override
    public boolean authenticate(String username, String password) {
        // Complex authentication logic
        if (username == null || password == null) {
            return false;
        }
        return this.username.equals(username) && validatePassword(password);
    }

    @Override
    public void logout() {
        System.out.println("Admin logged out");
    }

    private boolean validatePassword(String password) {
        return password.length() >= 8;
    }

    public void addPermission(String permission) {
        this.permissions.add(permission);
    }
}

/**
 * Generic session manager
 */
public class SessionManager<T extends User> {
    private Map<String, T> sessions;
    private static SessionManager<?> instance;

    private SessionManager() {
        this.sessions = new HashMap<>();
    }

    public static <T extends User> SessionManager<T> getInstance() {
        if (instance == null) {
            instance = new SessionManager<T>();
        }
        return (SessionManager<T>) instance;
    }

    public void createSession(String sessionId, T user) {
        sessions.put(sessionId, user);
    }

    public T getSession(String sessionId) {
        return sessions.get(sessionId);
    }
}

/**
 * Nested enum for status codes
 */
enum StatusCode {
    SUCCESS(200, "OK"),
    UNAUTHORIZED(401, "Unauthorized"),
    FORBIDDEN(403, "Forbidden"),
    NOT_FOUND(404, "Not Found");

    private final int code;
    private final String message;

    StatusCode(int code, String message) {
        this.code = code;
        this.message = message;
    }

    public int getCode() {
        return code;
    }
}
