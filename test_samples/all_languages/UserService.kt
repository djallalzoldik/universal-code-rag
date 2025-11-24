// Complex Kotlin file with advanced features
package com.example.app

import kotlinx.coroutines.*
import kotlin.reflect.KProperty

// Data class with default parameters
data class User(
    val id: Long,
    val username: String,
    val email: String,
    val roles: List<String> = emptyList()
)

// Sealed class hierarchy
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Interface with default implementation
interface Repository<T> {
    suspend fun findById(id: Long): Result<T>
    suspend fun findAll(): Result<List<T>>
    
    fun validate(item: T): Boolean = true
}

// Generic class with constraints
class UserRepository : Repository<User> {
    private val cache = mutableMapOf<Long, User>()
    
    override suspend fun findById(id: Long): Result<User> = withContext(Dispatchers.IO) {
        try {
            cache[id]?.let { Result.Success(it) }
                ?: Result.Error(Exception("User not found"))
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    override suspend fun findAll(): Result<List<User>> = withContext(Dispatchers.IO) {
        Result.Success(cache.values.toList())
    }
}

// Extension functions
fun <T> Result<T>.getOrNull(): T? = when (this) {
    is Result.Success -> data
    else -> null
}

inline fun <reified T> Result<T>.onSuccess(action: (T) -> Unit): Result<T> {
    if (this is Result.Success) action(data)
    return this
}

// Delegated properties
class LazyValue<T>(private val initializer: () -> T) {
    private var value: T? = null
    
    operator fun getValue(thisRef: Any?, property: KProperty<*>): T {
        if (value == null) {
            value = initializer()
        }
        return value!!
    }
}

// Object singleton
object Configuration {
    const val API_VERSION = "v1"
    val baseUrl by LazyValue { System.getenv("API_URL") ?: "http://localhost:8080" }
}

// Companion object
class UserService(private val repository: UserRepository) {
    companion object {
        private const val MAX_RETRIES = 3
        
        fun create(repo: UserRepository = UserRepository()): UserService {
            return UserService(repo)
        }
    }
    
    suspend fun getUser(id: Long): User? = repository.findById(id).getOrNull()
}

// Higher-order functions
suspend fun <T> retry(times: Int = 3, block: suspend () -> T): T {
    repeat(times - 1) {
        try {
            return block()
        } catch (e: Exception) {
            // Retry
        }
    }
    return block()
}
