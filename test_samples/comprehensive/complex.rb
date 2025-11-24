# Comprehensive Ruby test file with complex structures

module Authentication
  # Authenticator module
  module Authenticator
    def authenticate(username, password)
      raise NotImplementedError
    end
    
    def logout
      raise NotImplementedError
    end
  end
  
  # Base User class
  class User
    attr_reader :username, :id
    
    def initialize(username, id)
      @username = username
      @id = id
      @mutex = Mutex.new
    end
    
    def role
      raise NotImplementedError
    end
  end
  
  # AdminUser with mixed-in authenticator
  class AdminUser < User
    include Authenticator
    
    attr_accessor :permissions
    
    def initialize(username, id)
      super(username, id)
      @permissions = []
    end
    
    def role
      'ADMIN'
    end
    
    def authenticate(username, password)
      return false if username.nil? || password.nil?
      @username == username && valid_password?(password)
    end
    
    def logout
      puts 'Admin logged out'
    end
    
    def add_permission(permission)
      @mutex.synchronize do
        @permissions << permission
      end
    end
    
    private
    
    def valid_password?(password)
      password.length >= 8
    end
  end
  
  # Generic SessionManager class
  class SessionManager
    def initialize
      @sessions = {}
      @mutex = Mutex.new
    end
    
    def create_session(session_id, user)
      @mutex.synchronize do
        @sessions[session_id] = user
      end
    end
    
    def get_session(session_id)
      @mutex.synchronize do
        @sessions[session_id]
      end
    end
    
    def remove_session(session_id)
      @mutex.synchronize do
        @sessions.delete(session_id)
      end
    end
    
    # Singleton pattern
    class << self
      attr_accessor :instance
      
      def get_instance
        @instance ||= new
      end
    end
  end
  
  # Status code module
  module StatusCode
    SUCCESS = { code: 200, message: 'OK' }.freeze
    UNAUTHORIZED = { code: 401, message: 'Unauthorized' }.freeze
    FORBIDDEN = { code: 403, message: 'Forbidden' }.freeze
    NOT_FOUND = { code: 404, message: 'Not Found' }.freeze
    
    def self.get_message(code)
      constants.each do |const_name|
        const = const_get(const_name)
        return const[:message] if const[:code] == code
      end
      'Unknown'
    end
  end
end
