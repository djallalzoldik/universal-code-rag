// Comprehensive Go test file with complex structures
package complex

import (
	"fmt"
	"sync"
)

// Authenticator interface
type Authenticator interface {
	Authenticate(username, password string) bool
	Logout()
}

// User struct with embedding
type User struct {
	Username string
	ID       int
	mu       sync.RWMutex
}

// AdminUser embeds User
type AdminUser struct {
	User
	Permissions []string
}

// NewAdminUser constructor
func NewAdminUser(username string, id int) *AdminUser {
	return &AdminUser{
		User: User{
			Username: username,
			ID:       id,
		},
		Permissions: make([]string, 0),
	}
}

// Authenticate implements Authenticator
func (a *AdminUser) Authenticate(username, password string) bool {
	a.mu.RLock()
	defer a.mu.RUnlock()
	
	if username == "" || password == "" {
		return false
	}
	return a.Username == username && len(password) >= 8
}

// Logout implements Authenticator
func (a *AdminUser) Logout() {
	fmt.Println("Admin logged out")
}

// AddPermission adds a permission
func (a *AdminUser) AddPermission(perm string) {
	a.mu.Lock()
	defer a.mu.Unlock()
	a.Permissions = append(a.Permissions, perm)
}

// Generic session manager
type SessionManager[T any] struct {
	sessions map[string]T
	mu       sync.RWMutex
}

// NewSessionManager creates a new session manager
func NewSessionManager[T any]() *SessionManager[T] {
	return &SessionManager[T]{
		sessions: make(map[string]T),
	}
}

// CreateSession creates a new session
func (sm *SessionManager[T]) CreateSession(sessionID string, user T) {
	sm.mu.Lock()
	defer sm.mu.Unlock()
	sm.sessions[sessionID] = user
}

// GetSession retrieves a session
func (sm *SessionManager[T]) GetSession(sessionID string) (T, bool) {
	sm.mu.RLock()
	defer sm.mu.RUnlock()
	user, exists := sm.sessions[sessionID]
	return user, exists
}

// StatusCode type
type StatusCode int

const (
	Success StatusCode = iota
	Unauthorized
	Forbidden
	NotFound
)

// String method for StatusCode
func (sc StatusCode) String() string {
	switch sc {
	case Success:
		return "Success"
	case Unauthorized:
		return "Unauthorized"
	case Forbidden:
		return "Forbidden"
	case NotFound:
		return "NotFound"
	default:
		return "Unknown"
	}
}
