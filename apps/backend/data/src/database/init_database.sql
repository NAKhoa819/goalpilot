IF OBJECT_ID('goals', 'U') IS NULL
BEGIN
    CREATE TABLE goals (
        goal_id VARCHAR(50) PRIMARY KEY,
        goal_name NVARCHAR(255) NOT NULL,
        goal_type VARCHAR(50) NOT NULL,
        target_amount DECIMAL(15,2) NOT NULL,
        target_date DATE NOT NULL,
        currency VARCHAR(10) DEFAULT 'VND',
        status VARCHAR(50) DEFAULT 'on_track',
        created_from VARCHAR(50),
        created_at DATETIME DEFAULT GETDATE(),
        CONSTRAINT chk_goal_status CHECK (status IN ('on_track', 'at_risk', 'completed', 'paused')),
        CONSTRAINT chk_goal_type CHECK (goal_type IN ('purchase', 'saving', 'emergency_fund', 'custom'))
    );
END;
GO

IF OBJECT_ID('chat_sessions', 'U') IS NULL
BEGIN
    CREATE TABLE chat_sessions (
        session_id VARCHAR(50) PRIMARY KEY,
        created_at DATETIME DEFAULT GETDATE()
    );
END;
GO

IF OBJECT_ID('messages', 'U') IS NULL
BEGIN
    CREATE TABLE messages (
        message_id VARCHAR(50) PRIMARY KEY,
        session_id VARCHAR(50) NOT NULL,
        role VARCHAR(20) NOT NULL,
        text NVARCHAR(MAX),
        actions NVARCHAR(MAX),
        is_read BIT DEFAULT 0,
        created_at DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
        CONSTRAINT chk_role CHECK (role IN ('user', 'assistant')),
        CONSTRAINT chk_actions_json CHECK (actions IS NULL OR ISJSON(actions) = 1)
    );
END;
GO

IF OBJECT_ID('chat_session_state', 'U') IS NULL
BEGIN
    CREATE TABLE chat_session_state (
        session_id VARCHAR(50) PRIMARY KEY,
        state_json NVARCHAR(MAX) NOT NULL,
        updated_at DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
        CONSTRAINT chk_chat_session_state_json CHECK (ISJSON(state_json) = 1)
    );
END;
GO

IF OBJECT_ID('goal_action_state', 'U') IS NULL
BEGIN
    CREATE TABLE goal_action_state (
        goal_id VARCHAR(50) PRIMARY KEY,
        action_type VARCHAR(10) NOT NULL,
        strategy VARCHAR(50) NOT NULL,
        payload_json NVARCHAR(MAX) NOT NULL,
        updated_at DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (goal_id) REFERENCES goals(goal_id) ON DELETE CASCADE,
        CONSTRAINT chk_goal_action_type CHECK (action_type IN ('A', 'B')),
        CONSTRAINT chk_goal_action_payload_json CHECK (ISJSON(payload_json) = 1)
    );
END;
GO

IF OBJECT_ID('transactions', 'U') IS NULL
BEGIN
    CREATE TABLE transactions (
        transaction_id INT IDENTITY(1,1) PRIMARY KEY,
        [date] DATE NOT NULL,
        amount DECIMAL(15,2) NOT NULL,
        category VARCHAR(100),
        description NVARCHAR(255),
        is_essential BIT DEFAULT 0,
        source VARCHAR(50) DEFAULT 'manual',
        type VARCHAR(20) NOT NULL,
        goal_id VARCHAR(50),
        created_at DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (goal_id) REFERENCES goals(goal_id),
        CONSTRAINT chk_trans_type CHECK (type IN ('income', 'expense')),
        CONSTRAINT chk_trans_source CHECK (source IN ('manual'))
    );
END;
