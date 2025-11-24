-- Complex Haskell file with advanced features
{-# LANGUAGE GADTs #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE FlexibleInstances #-}

module UserService
    ( User(..)
    , UserRepository
    , findById
    , findAll
    , validateUser
    ) where

import Control.Monad (when)
import Data.Maybe (fromMaybe)
import qualified Data.Map as Map

-- Data types
data User = User
    { userId :: Int
    , username :: String
    , email :: String
    , roles :: [String]
    } deriving (Show, Eq)

-- Type synonyms
type UserId = Int
type UserMap = Map.Map UserId User

-- Newtype wrapper
newtype UserRepository = UserRepository { users :: UserMap }

-- Type classes
class Serializable a where
    serialize :: a -> String
    deserialize :: String -> Maybe a

instance Serializable User where
    serialize user = show user
    deserialize str = case reads str of
        [(user, "")] -> Just user
        _ -> Nothing

-- Higher-order functions
findById :: UserId -> UserRepository -> Maybe User
findById uid repo = Map.lookup uid (users repo)

findAll :: UserRepository -> [User]
findAll = Map.elems . users

filterUsers :: (User -> Bool) -> UserRepository -> [User]
filterUsers predicate = filter predicate . findAll

-- Pattern matching
validateUser :: User -> Either String User
validateUser user@(User _ uname email _)
    | null uname = Left "Username cannot be empty"
    | length uname < 3 = Left "Username too short"
    | '@' `notElem` email = Left "Invalid email"
    | otherwise = Right user

-- Monadic operations
saveUser :: User -> UserRepository -> Either String UserRepository
saveUser user repo = do
    validUser <- validateUser user
    return $ UserRepository $ Map.insert (userId validUser) validUser (users repo)

-- List comprehensions
getUsersByRole :: String -> UserRepository -> [User]
getUsersByRole role repo = 
    [ user | user <- findAll repo, role `elem` roles user ]

-- Recursive functions
countUsers :: UserRepository -> Int
countUsers = Map.size . users

-- Applicative functors
type ValidationResult a = Either [String] a

validateUsername :: String -> ValidationResult String
validateUsername name
    | null name = Left ["Username cannot be empty"]
    | length name < 3 = Left ["Username too short"]
    | otherwise = Right name

validateEmail :: String -> ValidationResult String
validateEmail email
    | '@' `elem` email = Right email
    | otherwise = Left ["Invalid email format"]

-- Function composition
processUser :: User -> String
processUser = serialize . fromMaybe (User 0 "" "" []) . Just

-- GADTs
data Expr a where
    IntLit :: Int -> Expr Int
    BoolLit :: Bool -> Expr Bool
    Add :: Expr Int -> Expr Int -> Expr Int
    Equals :: Eq a => Expr a -> Expr a -> Expr Bool

eval :: Expr a -> a
eval (IntLit n) = n
eval (BoolLit b) = b
eval (Add e1 e2) = eval e1 + eval e2
eval (Equals e1 e2) = eval e1 == eval e2
