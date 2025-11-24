// Comprehensive C++ test file with complex structures
#ifndef COMPLEX_CPP_TEST_H_
#define COMPLEX_CPP_TEST_H_

#include <memory>
#include <string>
#include <vector>
#include <map>
#include <mutex>

namespace authentication {
namespace complex {

// Forward declarations
class User;
class AdminUser;

// Interface (abstract class in C++)
class Authenticator {
 public:
  virtual ~Authenticator() = default;
  virtual bool Authenticate(const std::string& username, const std::string& password) = 0;
  virtual void Logout() = 0;
};

// Base User class
class User {
 public:
  User(const std::string& username, int id) 
      : username_(username), id_(id) {}
  virtual ~User() = default;
  
  virtual std::string GetRole() const = 0;
  const std::string& GetUsername() const { return username_; }
  int GetId() const { return id_; }
  
 protected:
  std::string username_;
  int id_;
  mutable std::mutex mutex_;
};

// AdminUser with multiple inheritance
class AdminUser : public User, public Authenticator {
 public:
  AdminUser(const std::string& username, int id);
  ~AdminUser() override;
  
  // Override User
  std::string GetRole() const override { return "ADMIN"; }
  
  // Implement Authenticator
  bool Authenticate(const std::string& username, const std::string& password) override;
  void Logout() override;
  
  // Admin-specific methods
  void AddPermission(const std::string& permission);
  const std::vector<std::string>& GetPermissions() const;
  
 private:
  bool ValidatePassword(const std::string& password) const;
  
  std::vector<std::string> permissions_;
};

// Template SessionManager
template<typename T>
class SessionManager {
 public:
  static SessionManager<T>* GetInstance() {
    static SessionManager<T> instance;
    return &instance;
  }
  
  void CreateSession(const std::string& session_id, std::shared_ptr<T> user) {
    std::lock_guard<std::mutex> lock(mutex_);
    sessions_[session_id] = user;
  }
  
  std::shared_ptr<T> GetSession(const std::string& session_id) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = sessions_.find(session_id);
    return (it != sessions_.end()) ? it->second : nullptr;
  }
  
  void RemoveSession(const std::string& session_id) {
    std::lock_guard<std::mutex> lock(mutex_);
    sessions_.erase(session_id);
  }
  
 private:
  SessionManager() = default;
  ~SessionManager() = default;
  SessionManager(const SessionManager&) = delete;
  SessionManager& operator=(const SessionManager&) = delete;
  
  std::map<std::string, std::shared_ptr<T>> sessions_;
  std::mutex mutex_;
};

// Enum class
enum class StatusCode {
  kSuccess = 200,
  kUnauthorized = 401,
  kForbidden = 403,
  kNotFound = 404
};

// Helper function
const char* GetStatusMessage(StatusCode code);

// Complex template function
template<typename T>
std::pair<bool, std::string> AuthenticateAndCreateSession(
    std::shared_ptr<T> user,
    const std::string& username,
    const std::string& password,
    SessionManager<T>* manager) {
  static_assert(std::is_base_of<Authenticator, T>::value, 
                "T must inherit from Authenticator");
  
  if (user->Authenticate(username, password)) {
    // Generate session ID (simplified)
    std::string session_id = "session_" + username;
    manager->CreateSession(session_id, user);
    return {true, session_id};
  }
  return {false, ""};
}

}  // namespace complex
}  // namespace authentication

#endif  // COMPLEX_CPP_TEST_H_
