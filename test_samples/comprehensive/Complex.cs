// Comprehensive C# test file with complex structures
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;

namespace Authentication.Complex
{
    /// <summary>
    /// Authenticator interface
    /// </summary>
    public interface IAuthenticator
    {
        bool Authenticate(string username, string password);
        void Logout();
    }
    
    /// <summary>
    /// Base User class
    /// </summary>
    public abstract class User
    {
        protected string Username { get; set; }
        protected int Id { get; set; }
        
        public User(string username, int id)
        {
            Username = username;
            Id = id;
        }
        
        public abstract string GetRole();
    }
    
    /// <summary>
    /// AdminUser with interface implementation
    /// </summary>
    public class AdminUser : User, IAuthenticator
    {
        private List<string> _permissions;
        private readonly ReaderWriterLockSlim _lock;
        
        public AdminUser(string username, int id) : base(username, id)
        {
            _permissions = new List<string>();
            _lock = new ReaderWriterLockSlim();
        }
        
        public override string GetRole()
        {
            return "ADMIN";
        }
        
        public bool Authenticate(string username, string password)
        {
            if (string.IsNullOrEmpty(username) || string.IsNullOrEmpty(password))
            {
                return false;
            }
            return Username == username && ValidatePassword(password);
        }
        
        public void Logout()
        {
            Console.WriteLine("Admin logged out");
        }
        
        public void AddPermission(string permission)
        {
            _lock.EnterWriteLock();
            try
            {
                _permissions.Add(permission);
            }
            finally
            {
                _lock.ExitWriteLock();
            }
        }
        
        private bool ValidatePassword(string password)
        {
            return password.Length >= 8;
        }
    }
    
    /// <summary>
    /// Generic SessionManager
    /// </summary>
    public class SessionManager<T> where T : User
    {
        private static SessionManager<T> _instance;
        private static readonly object _lock = new object();
        private Dictionary<string, T> _sessions;
        
        private SessionManager()
        {
            _sessions = new Dictionary<string, T>();
        }
        
        public static SessionManager<T> GetInstance()
        {
            if (_instance == null)
            {
                lock (_lock)
                {
                    if (_instance == null)
                    {
                        _instance = new SessionManager<T>();
                    }
                }
            }
            return _instance;
        }
        
        public void CreateSession(string sessionId, T user)
        {
            lock (_lock)
            {
                _sessions[sessionId] = user;
            }
        }
        
        public T GetSession(string sessionId)
        {
            lock (_lock)
            {
                return _sessions.TryGetValue(sessionId, out var user) ? user : null;
            }
        }
    }
    
    /// <summary>
    /// StatusCode enum
    /// </summary>
    public enum StatusCode
    {
        Success = 200,
        Unauthorized = 401,
        Forbidden = 403,
        NotFound = 404
    }
    
    /// <summary>
    /// Extension methods for StatusCode
    /// </summary>
    public static class StatusCodeExtensions
    {
        public static string GetMessage(this StatusCode code)
        {
            return code switch
            {
                StatusCode.Success => "OK",
                StatusCode.Unauthorized => "Unauthorized",
                StatusCode.Forbidden => "Forbidden",
                StatusCode.NotFound => "Not Found",
                _ => "Unknown"
            };
        }
    }
    
    /// <summary>
    /// Complex authentication service
    /// </summary>
    public class AuthenticationService
    {
        public (bool success, string sessionId) AuthenticateAndCreateSession<T>(
            T user,
            string username,
            string password,
            SessionManager<T> manager
        ) where T : User, IAuthenticator
        {
            if (user.Authenticate(username, password))
            {
                var sessionId = Guid.NewGuid().ToString();
                manager.CreateSession(sessionId, user);
                return (true, sessionId);
            }
            return (false, null);
        }
    }
}
