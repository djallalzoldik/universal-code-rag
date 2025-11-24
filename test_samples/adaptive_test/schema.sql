-- SQL Test for QUERY_BASED Architecture

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create posts table
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    content TEXT,
    published_at TIMESTAMP
);

-- Query active users
SELECT u.username, COUNT(p.id) as post_count
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
WHERE p.published_at > NOW() - INTERVAL '30 days'
GROUP BY u.username
HAVING COUNT(p.id) > 5
ORDER BY post_count DESC;

-- Create index for performance
CREATE INDEX idx_posts_user_published ON posts(user_id, published_at);
