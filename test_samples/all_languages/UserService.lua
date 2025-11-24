-- Complex Lua script with advanced features

-- Module definition
local UserService = {}
UserService.__index = UserService

-- Constructor
function UserService:new(repository)
    local instance = setmetatable({}, UserService)
    instance.repository = repository
    instance.cache = {}
    return instance
end

-- Metatable for User
local User = {}
User.__index = User

function User:new(id, username, email)
    return setmetatable({
        id = id,
        username = username,
        email = email,
        created_at = os.time()
    }, User)
end

function User:validate()
    if not self.username or #self.username < 3 then
        return false, "Username too short"
    end
    if not self.email or not self.email:match("@") then
        return false, "Invalid email"
    end
    return true
end

-- Class methods
function UserService:findById(id)
    -- Check cache first
    if self.cache[id] then
        return self.cache[id]
    end
    
    -- Fetch from repository
    local user = self.repository:findById(id)
    if user then
        self.cache[id] = user
    end
    return user
end

function UserService:findAll(options)
    options = options or {}
    local limit = options.limit or 100
    local offset = options.offset or 0
    
    return self.repository:findAll(limit, offset)
end

-- Higher-order function
function UserService:map(users, fn)
    local result = {}
    for i, user in ipairs(users) do
        table.insert(result, fn(user))
    end
    return result
end

-- Coroutine example
function UserService:processAsync(userId, callback)
    local co = coroutine.create(function()
        local user = self:findById(userId)
        if user then
            callback(nil, user)
        else
            callback("User not found")
        end
    end)
    
    return coroutine.resume(co)
end

-- Closure example
function UserService:createValidator(minLength)
    return function(username)
        return #username >= minLength
    end
end

-- Table manipulation
local function deepCopy(orig)
    local copy
    if type(orig) == 'table' then
        copy = {}
        for k, v in pairs(orig) do
            copy[deepCopy(k)] = deepCopy(v)
        end
    else
        copy = orig
    end
    return copy
end

-- Module exports
return {
    UserService = UserService,
    User = User,
    deepCopy = deepCopy
}
