// Comprehensive Rust test file with complex structures
use std::collections::HashMap;
use std::sync::{Arc, RwLock};

/// Authenticator trait
pub trait Authenticator {
    fn authenticate(&self, username: &str, password: &str) -> bool;
    fn logout(&self);
}

/// Base User struct
#[derive(Debug, Clone)]
pub struct User {
    pub username: String,
    pub id: u32,
}

impl User {
    pub fn new(username: String, id: u32) -> Self {
        User { username, id }
    }
}

/// AdminUser with permissions
#[derive(Debug, Clone)]
pub struct AdminUser {
    user: User,
    permissions: Vec<String>,
}

impl AdminUser {
    pub fn new(username: String, id: u32) -> Self {
        AdminUser {
            user: User::new(username, id),
            permissions: Vec::new(),
        }
    }
    
    pub fn add_permission(&mut self, permission: String) {
        self.permissions.push(permission);
    }
    
    fn validate_password(&self, password: &str) -> bool {
        password.len() >= 8
    }
}

impl Authenticator for AdminUser {
    fn authenticate(&self, username: &str, password: &str) -> bool {
        if username.is_empty() || password.is_empty() {
            return false;
        }
        self.user.username == username && self.validate_password(password)
    }
    
    fn logout(&self) {
        println!("Admin logged out");
    }
}

/// Generic SessionManager
pub struct SessionManager<T> {
    sessions: Arc<RwLock<HashMap<String, T>>>,
}

impl<T: Clone> SessionManager<T> {
    pub fn new() -> Self {
        SessionManager {
            sessions: Arc::new(RwLock::new(HashMap::new())),
        }
    }
    
    pub fn create_session(&self, session_id: String, user: T) {
        let mut sessions = self.sessions.write().unwrap();
        sessions.insert(session_id, user);
    }
    
    pub fn get_session(&self, session_id: &str) -> Option<T> {
        let sessions = self.sessions.read().unwrap();
        sessions.get(session_id).cloned()
    }
}

/// Status code enum
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum StatusCode {
    Success = 200,
    Unauthorized = 401,
    Forbidden = 403,
    NotFound = 404,
}

impl StatusCode {
    pub fn message(&self) -> &'static str {
        match self {
            StatusCode::Success => "OK",
            StatusCode::Unauthorized => "Unauthorized",
            StatusCode::Forbidden => "Forbidden",
            StatusCode::NotFound => "Not Found",
        }
    }
}

/// Result type alias
pub type AuthResult<T> = Result<T, StatusCode>;

/// Complex function with error handling
pub fn authenticate_and_create_session<T: Authenticator + Clone>(
    user: &T,
    username: &str,
    password: &str,
    manager: &SessionManager<T>,
) -> AuthResult<String> {
    if user.authenticate(username, password) {
        let session_id = format!("session_{}", uuid::Uuid::new_v4());
        manager.create_session(session_id.clone(), user.clone());
        Ok(session_id)
    } else {
        Err(StatusCode::Unauthorized)
    }
}
