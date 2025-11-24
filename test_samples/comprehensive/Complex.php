<?php
// Comprehensive PHP test file with complex structures

namespace Authentication;

/**
 * Authenticator interface
 */
interface Authenticator {
    public function authenticate(string $username, string $password): bool;
    public function logout(): void;
}

/**
 * Loggable trait
 */
trait Loggable {
    protected function log(string $message): void {
        echo "[LOG] $message\n";
    }
}

/**
 * Base User class
 */
abstract class User {
    protected string $username;
    protected int $id;
    
    public function __construct(string $username, int $id) {
        $this->username = $username;
        $this->id = $id;
    }
    
    abstract public function getRole(): string;
    
    public function getUsername(): string {
        return $this->username;
    }
}

/**
 * AdminUser class with trait and interface
 */
class AdminUser extends User implements Authenticator {
    use Loggable;
    
    private array $permissions = [];
    
    public function __construct(string $username, int $id) {
        parent::__construct($username, $id);
        $this->log("Admin user created: $username");
    }
    
    public function getRole(): string {
        return 'ADMIN';
    }
    
    public function authenticate(string $username, string $password): bool {
        if (empty($username) || empty($password)) {
            return false;
        }
        return $this->username === $username && $this->validatePassword($password);
    }
    
    public function logout(): void {
        $this->log("Admin logged out: {$this->username}");
    }
    
    public function addPermission(string $permission): void {
        $this->permissions[] = $permission;
        $this->log("Permission added: $permission");
    }
    
    private function validatePassword(string $password): bool {
        return strlen($password) >= 8;
    }
}

/**
 * Generic SessionManager class
 */
class SessionManager {
    private static ?SessionManager $instance = null;
    private array $sessions = [];
    
    private function __construct() {}
    
    public static function getInstance(): SessionManager {
        if (self::$instance === null) {
            self::$instance = new SessionManager();
        }
        return self::$instance;
    }
    
    public function createSession(string $sessionId, User $user): void {
        $this->sessions[$sessionId] = $user;
    }
    
    public function getSession(string $sessionId): ?User {
        return $this->sessions[$sessionId] ?? null;
    }
    
    public function removeSession(string $sessionId): void {
        unset($this->sessions[$sessionId]);
    }
}

/**
 * StatusCode enum (PHP 8.1+)
 */
enum StatusCode: int {
    case SUCCESS = 200;
    case UNAUTHORIZED = 401;
    case FORBIDDEN = 403;
    case NOT_FOUND = 404;
    
    public function getMessage(): string {
        return match($this) {
            self::SUCCESS => 'OK',
            self::UNAUTHORIZED => 'Unauthorized',
            self::FORBIDDEN => 'Forbidden',
            self::NOT_FOUND => 'Not Found',
        };
    }
}

/**
 * Complex function with type hints
 */
function authenticateAndCreateSession(
    Authenticator $user,
    string $username,
    string $password,
    SessionManager $manager
): array {
    if ($user->authenticate($username, $password)) {
        $sessionId = uniqid('session_', true);
        $manager->createSession($sessionId, $user);
        return ['success' => true, 'sessionId' => $sessionId];
    }
    return ['success' => false, 'error' => StatusCode::UNAUTHORIZED->getMessage()];
}
