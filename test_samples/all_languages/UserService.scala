// Complex Scala file with advanced features
package com.example.app

import scala.concurrent.{Future, ExecutionContext}
import scala.util.{Try, Success, Failure}

// Case classes
case class User(id: Long, username: String, email: String)
case class Post(id: Long, userId: Long, title: String, content: String)

// Sealed trait (similar to sealed class in Kotlin)
sealed trait Result[+A]
case class Ok[A](value: A) extends Result[A]
case class Err(message: String) extends Result[Nothing]
case object Loading extends Result[Nothing]

// Trait with type parameters
trait Repository[T] {
  def findById(id: Long): Future[Option[T]]
  def findAll(): Future[Seq[T]]
  def save(entity: T): Future[T]
}

// Implicit parameters and type classes
trait JsonSerializer[T] {
  def toJson(value: T): String
}

object JsonSerializer {
  implicit val userSerializer: JsonSerializer[User] = new JsonSerializer[User] {
    def toJson(user: User): String = 
      s"""{"id":${user.id},"username":"${user.username}","email":"${user.email}"}"""
  }
}

// Generic class with implicit evidence
class UserRepository(implicit ec: ExecutionContext) extends Repository[User] {
  private var users = Map.empty[Long, User]
  
  override def findById(id: Long): Future[Option[User]] = Future {
    users.get(id)
  }
  
  override def findAll(): Future[Seq[User]] = Future {
    users.values.toSeq
  }
  
  override def save(user: User): Future[User] = Future {
    users = users + (user.id -> user)
    user
  }
}

// Pattern matching and for-comprehensions
class UserService(repository: Repository[User])(implicit ec: ExecutionContext) {
  def getUserWithPosts(userId: Long): Future[Result[(User, Seq[Post])]] = {
    val result = for {
      userOpt <- repository.findById(userId)
      user <- Future.successful(userOpt)
      // Simulated post retrieval
      posts = Seq.empty[Post]
    } yield (user, posts)
    
    result.map {
      case Some(data) => Ok(data)
      case None => Err("User not found")
    }.recover {
      case ex: Exception => Err(ex.getMessage)
    }
  }
  
  // Higher-order functions
  def processUsers(predicate: User => Boolean): Future[Seq[User]] = {
    repository.findAll().map(_.filter(predicate))
  }
}

// Companion object with apply method
object UserService {
  def apply(repository: Repository[User])(implicit ec: ExecutionContext): UserService = {
    new UserService(repository)
  }
}

// Type aliases and implicit conversions
type UserId = Long
type Username = String

object Converters {
  implicit class UserOps(user: User) {
    def toJson(implicit serializer: JsonSerializer[User]): String = {
      serializer.toJson(user)
    }
  }
}

// Partial functions
object UserValidator {
  val isValidEmail: PartialFunction[User, Boolean] = {
    case User(_, _, email) if email.contains("@") => true
  }
  
  val isValidUsername: PartialFunction[User, Boolean] = {
    case User(_, username, _) if username.length >= 3 => true
  }
  
  val validate: PartialFunction[User, Boolean] = 
    isValidEmail orElse isValidUsername
}
