-- ============================================================
-- Bingo Bash-Style F2P Game Analytics — Schema
-- Portfolio project: A/B Test & Player Engagement Analytics
-- ============================================================

CREATE TABLE players (
    player_id           INT PRIMARY KEY,
    install_date         DATE NOT NULL,
    country              VARCHAR(2) NOT NULL,        -- ISO country code
    platform             VARCHAR(10) NOT NULL,        -- iOS / Android
    acquisition_channel   VARCHAR(20) NOT NULL,        -- organic / paid_social / paid_search / cross_promo
    spend_tier           VARCHAR(10) NOT NULL,        -- non_payer / minnow / dolphin / whale
    ab_test_variant      VARCHAR(1)                    -- 'A' (control) / 'B' (treatment)
);

CREATE TABLE sessions (
    session_id           BIGINT PRIMARY KEY,
    player_id             INT NOT NULL REFERENCES players(player_id),
    session_start         DATETIME NOT NULL,
    session_length_sec    INT NOT NULL,
    rounds_played         INT NOT NULL
);

CREATE TABLE bingo_rounds (
    round_id              BIGINT PRIMARY KEY,
    session_id             BIGINT NOT NULL REFERENCES sessions(session_id),
    player_id              INT NOT NULL REFERENCES players(player_id),
    round_timestamp        DATETIME NOT NULL,
    room_type              VARCHAR(20) NOT NULL,       -- classic / speed / jackpot
    won                    BOOLEAN NOT NULL,
    coins_wagered          INT NOT NULL,
    coins_won              INT NOT NULL
);

CREATE TABLE bonus_events (
    bonus_id              BIGINT PRIMARY KEY,
    player_id              INT NOT NULL REFERENCES players(player_id),
    bonus_timestamp         DATETIME NOT NULL,
    bonus_type              VARCHAR(20) NOT NULL,      -- daily_login / power_up / jackpot_wheel / streak
    coins_awarded           INT NOT NULL,
    ab_test_variant          VARCHAR(1)                 -- redundant copy for query convenience
);

CREATE TABLE iap_transactions (
    transaction_id         BIGINT PRIMARY KEY,
    player_id               INT NOT NULL REFERENCES players(player_id),
    transaction_timestamp   DATETIME NOT NULL,
    product_type             VARCHAR(20) NOT NULL,      -- coin_pack / power_up / starter_bundle / vip_pass
    usd_amount               DECIMAL(6,2) NOT NULL
);

CREATE TABLE ab_test_assignments (
    player_id               INT PRIMARY KEY REFERENCES players(player_id),
    test_name                 VARCHAR(50) NOT NULL,      -- e.g. 'bonus_wheel_variance_test'
    variant                   VARCHAR(1) NOT NULL,        -- A / B
    assignment_date            DATE NOT NULL
);

-- Indexes for common query patterns
CREATE INDEX idx_sessions_player ON sessions(player_id);
CREATE INDEX idx_rounds_player ON bingo_rounds(player_id);
CREATE INDEX idx_bonus_player ON bonus_events(player_id);
CREATE INDEX idx_iap_player ON iap_transactions(player_id);
CREATE INDEX idx_sessions_date ON sessions(session_start);
