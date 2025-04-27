-- CREATE database farpost;
USE farpost;

-- Таблица пользователей
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (username)
);

-- Таблица тем
CREATE TABLE threads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    creator_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    deleted_at DATETIME DEFAULT NULL,
    FOREIGN KEY (creator_id) REFERENCES users(id)
        ON DELETE CASCADE
);

-- Таблица сообщений
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    thread_id INT NOT NULL,
    author_id INT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (thread_id) REFERENCES threads(id)
        ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id)
        ON DELETE SET NULL
);

-- Таблица логов
CREATE TABLE logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    action_type ENUM(
        'first_visit', 'register', 'login', 'logout',
        'create_thread', 'visit_thread', 'delete_thread', 'post_message'
    ) NOT NULL,
    target_id INT NULL,
    target_type ENUM('thread', 'message', 'none') DEFAULT 'none',
    status ENUM('success', 'error') NOT NULL,
    message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE SET NULL
);
