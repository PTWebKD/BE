-- ============================================================
-- FitFuel+ Database Schema
-- Database: PostgreSQL 15+
-- Tác giả: FitFuel+ Team
-- Ngày: 2026-05-11
-- ============================================================

-- Xoá database cũ nếu cần (chỉ dùng khi reset hoàn toàn)
-- DROP SCHEMA public CASCADE; CREATE SCHEMA public;

-- ============================================================
-- BƯỚC 1: TẠO CÁC KIỂU ENUM
-- ============================================================

CREATE TYPE user_role     AS ENUM ('member', 'vendor', 'gym_owner');
CREATE TYPE fitness_goal  AS ENUM ('bulk', 'cut', 'maintain');
CREATE TYPE session_status AS ENUM ('active', 'done', 'cancelled');
CREATE TYPE muscle_group  AS ENUM ('chest', 'back', 'legs', 'shoulders', 'arms', 'core');
CREATE TYPE order_status  AS ENUM ('pending', 'confirmed', 'preparing', 'delivering', 'delivered', 'cancelled');
CREATE TYPE gear_category AS ENUM ('Weights', 'Apparel', 'Supplements', 'Accessories', 'Cardio', 'Recovery');
CREATE TYPE listing_type  AS ENUM ('sell', 'rent', 'both');
CREATE TYPE lifecycle_action AS ENUM ('listed', 'sold', 'rented', 'returned', 'relisted');
CREATE TYPE gear_txn_type AS ENUM ('sale', 'rental');
CREATE TYPE gear_txn_status AS ENUM ('pending', 'active', 'completed', 'disputed');
CREATE TYPE membership_status AS ENUM ('active', 'expired', 'cancelled');
CREATE TYPE challenge_type AS ENUM ('weekly', 'monthly', 'special');
CREATE TYPE user_challenge_status AS ENUM ('in_progress', 'completed', 'failed');
CREATE TYPE badge_category AS ENUM ('gym', 'food', 'gear', 'social', 'streak');
CREATE TYPE fitcoin_type   AS ENUM ('earn', 'spend', 'deposit', 'refund');
CREATE TYPE fitcoin_source AS ENUM (
  'gear_sale', 'challenge', 'referral', 'streak',
  'deposit', 'food_order', 'gear_rental', 'membership'
);
CREATE TYPE post_type AS ENUM ('milestone', 'pr', 'streak', 'transformation', 'review');
CREATE TYPE notif_type AS ENUM (
  'streak_reminder', 'order_update', 'promo',
  'challenge', 'gear_return', 'gym_closed', 'gear_approved'
);

-- ============================================================
-- BƯỚC 2: TẠO BẢNG (theo thứ tự phụ thuộc FK)
-- ============================================================

-- ------------------------------------------------------------
-- 1. USERS — Bảng trung tâm
-- ------------------------------------------------------------
CREATE TABLE users (
  user_id          SERIAL          PRIMARY KEY,
  email            VARCHAR(255)    NOT NULL UNIQUE,
  phone            VARCHAR(15)     UNIQUE,
  password_hash    VARCHAR(255)    NOT NULL,
  role             user_role       NOT NULL DEFAULT 'member',
  display_name     VARCHAR(100)    NOT NULL,
  avatar_url       VARCHAR(500),
  fitness_goal     fitness_goal,
  xp_total         INT             NOT NULL DEFAULT 0 CHECK (xp_total >= 0),
  current_level    INT             NOT NULL DEFAULT 1 CHECK (current_level >= 1),
  current_streak   INT             NOT NULL DEFAULT 0 CHECK (current_streak >= 0),
  fitcoin_balance  DECIMAL(12,2)   NOT NULL DEFAULT 0 CHECK (fitcoin_balance >= 0),
  tdee             INT             CHECK (tdee > 0),
  referred_by      INT             REFERENCES users(user_id) ON DELETE SET NULL,
  last_active_date DATE,
  allergens        JSONB           NOT NULL DEFAULT '[]',
  created_at       TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_role  ON users(role);

-- ------------------------------------------------------------
-- 2. FITNESS_PASSPORT — Quan hệ 1:1 với USERS
-- ------------------------------------------------------------
CREATE TABLE fitness_passport (
  passport_id      SERIAL          PRIMARY KEY,
  user_id          INT             NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
  total_sessions   INT             NOT NULL DEFAULT 0,
  total_volume     DECIMAL(12,2)   NOT NULL DEFAULT 0,
  longest_streak   INT             NOT NULL DEFAULT 0,
  body_weight_log  JSONB           DEFAULT '[]',
  body_photos      JSONB           DEFAULT '[]',
  milestone_badges JSONB           DEFAULT '[]',
  is_public        BOOLEAN         NOT NULL DEFAULT true,
  created_at       TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- 3. FOLLOWS — Quan hệ N:N user tự follow nhau
-- ------------------------------------------------------------
CREATE TABLE follows (
  follower_id      INT             NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  following_id     INT             NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  created_at       TIMESTAMP       NOT NULL DEFAULT NOW(),
  PRIMARY KEY (follower_id, following_id),
  CONSTRAINT no_self_follow CHECK (follower_id <> following_id)
);

-- ------------------------------------------------------------
-- 4. GYMS — Phòng tập của Gym Owner
-- ------------------------------------------------------------
CREATE TABLE gyms (
  gym_id           SERIAL          PRIMARY KEY,
  owner_id         INT             NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  name             VARCHAR(200)    NOT NULL,
  address          VARCHAR(500)    NOT NULL,
  phone            VARCHAR(15),
  opening_hours    JSONB           DEFAULT '{}',
  services         JSONB           DEFAULT '[]',
  membership_plans JSONB           DEFAULT '[]',
  logo_url         VARCHAR(500),
  created_at       TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_gyms_owner ON gyms(owner_id);

-- ------------------------------------------------------------
-- 5. GYM_MEMBERSHIPS — Thẻ hội viên của user tại gym
-- ------------------------------------------------------------
CREATE TABLE gym_memberships (
  membership_id    SERIAL          PRIMARY KEY,
  user_id          INT             NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  gym_id           INT             NOT NULL REFERENCES gyms(gym_id) ON DELETE CASCADE,
  plan_name        VARCHAR(100)    NOT NULL,
  start_date       DATE            NOT NULL,
  end_date         DATE            NOT NULL,
  status           membership_status NOT NULL DEFAULT 'active',
  auto_renew       BOOLEAN         NOT NULL DEFAULT false,
  payment_method   VARCHAR(50),
  amount_paid      DECIMAL(12,2)   NOT NULL DEFAULT 0,
  created_at       TIMESTAMP       NOT NULL DEFAULT NOW(),
  CONSTRAINT valid_dates CHECK (end_date > start_date)
);

CREATE INDEX idx_memberships_user ON gym_memberships(user_id);
CREATE INDEX idx_memberships_gym  ON gym_memberships(gym_id);

-- ------------------------------------------------------------
-- 6. WORKOUT_SESSIONS — Mỗi buổi tập
-- ------------------------------------------------------------
CREATE TABLE workout_sessions (
  session_id       SERIAL          PRIMARY KEY,
  user_id          INT             NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  gym_id           INT             REFERENCES gyms(gym_id) ON DELETE SET NULL,
  date             DATE            NOT NULL,
  duration_min     INT             CHECK (duration_min > 0),
  status           session_status  NOT NULL DEFAULT 'active',
  notes            TEXT,
  created_at       TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_date ON workout_sessions(user_id, date DESC);

-- ------------------------------------------------------------
-- 7. EXERCISE_LOGS — Chi tiết bài tập trong 1 session
-- ------------------------------------------------------------
CREATE TABLE exercise_logs (
  log_id           SERIAL          PRIMARY KEY,
  session_id       INT             NOT NULL REFERENCES workout_sessions(session_id) ON DELETE CASCADE,
  exercise_name    VARCHAR(200)    NOT NULL,
  muscle_group     muscle_group    NOT NULL,
  -- JSON: [{"reps": 10, "weight": 60}, {"reps": 8, "weight": 65}]
  sets             JSONB           NOT NULL DEFAULT '[]',
  is_pr            BOOLEAN         NOT NULL DEFAULT false,
  notes            TEXT,
  created_at       TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_logs_session ON exercise_logs(session_id);

-- ------------------------------------------------------------
-- 8. FOOD_PRODUCTS — Món ăn healthy của vendor
-- ------------------------------------------------------------
CREATE TABLE food_products (
  product_id       SERIAL          PRIMARY KEY,
  vendor_id        INT             NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  name             VARCHAR(200)    NOT NULL,
  description      TEXT,
  price            DECIMAL(10,2)   NOT NULL CHECK (price > 0),
  calories         INT             NOT NULL CHECK (calories >= 0),
  protein_g        DECIMAL(5,1)    NOT NULL DEFAULT 0 CHECK (protein_g >= 0),
  carb_g           DECIMAL(5,1)    NOT NULL DEFAULT 0 CHECK (carb_g >= 0),
  fat_g            DECIMAL(5,1)    NOT NULL DEFAULT 0 CHECK (fat_g >= 0),
  ingredients      JSONB           DEFAULT '[]',
  allergens        JSONB           DEFAULT '[]',
  images           JSONB           NOT NULL DEFAULT '[]',
  category         VARCHAR(50),
  badge            VARCHAR(50),
  is_available     BOOLEAN         NOT NULL DEFAULT true,
  avg_rating       DECIMAL(2,1)    NOT NULL DEFAULT 0 CHECK (avg_rating BETWEEN 0 AND 5),
  total_reviews    INT             NOT NULL DEFAULT 0,
  total_orders     INT             NOT NULL DEFAULT 0,
  created_at       TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_food_vendor    ON food_products(vendor_id);
CREATE INDEX idx_food_available ON food_products(is_available);

-- ------------------------------------------------------------
-- 9. FOOD_ORDERS — Đơn hàng (cả Member lẫn Guest)
-- ------------------------------------------------------------
CREATE TABLE food_orders (
  order_id         SERIAL          PRIMARY KEY,
  user_id          INT             REFERENCES users(user_id) ON DELETE SET NULL, -- NULL = Guest
  guest_phone      VARCHAR(15),
  vendor_id        INT             NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  -- JSON: [{"product_id": 1, "qty": 2, "price": 89000, "name": "Power Protein Bowl"}]
  items            JSONB           NOT NULL,
  subtotal         DECIMAL(12,2)   NOT NULL CHECK (subtotal >= 30000),
  delivery_fee     DECIMAL(10,2)   NOT NULL DEFAULT 15000,
  total_amount     DECIMAL(12,2)   NOT NULL CHECK (total_amount > 0),
  fitcoin_used     DECIMAL(12,2)   NOT NULL DEFAULT 0,
  delivery_address VARCHAR(500)    NOT NULL,
  delivery_time    VARCHAR(50),
  status           order_status    NOT NULL DEFAULT 'pending',
  payment_method   VARCHAR(50),
  is_meal_prep     BOOLEAN         NOT NULL DEFAULT false,
  created_at       TIMESTAMP       NOT NULL DEFAULT NOW(),
  CONSTRAINT guest_or_member CHECK (
    user_id IS NOT NULL OR guest_phone IS NOT NULL
  )
);

CREATE INDEX idx_orders_user   ON food_orders(user_id);
CREATE INDEX idx_orders_vendor ON food_orders(vendor_id);
CREATE INDEX idx_orders_status ON food_orders(status);

-- ------------------------------------------------------------
-- 10. FOOD_REVIEWS — Đánh giá món ăn
-- ------------------------------------------------------------
CREATE TABLE food_reviews (
  review_id        SERIAL          PRIMARY KEY,
  product_id       INT             NOT NULL REFERENCES food_products(product_id) ON DELETE CASCADE,
  user_id          INT             NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  rating           INT             NOT NULL CHECK (rating BETWEEN 1 AND 5),
  comment          TEXT,
  photos           JSONB           DEFAULT '[]',
  helpful_votes    INT             NOT NULL DEFAULT 0,
  created_at       TIMESTAMP       NOT NULL DEFAULT NOW(),
  UNIQUE (product_id, user_id)    -- Mỗi user chỉ review 1 lần/sản phẩm
);

-- ------------------------------------------------------------
-- 11. GEAR_ITEMS — Thiết bị gym trên Gear Hub
-- ------------------------------------------------------------
CREATE TABLE gear_items (
  gear_id              VARCHAR(20)     PRIMARY KEY, -- GEAR-XXXX-XXXX
  current_owner_id     INT             NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  -- Lister là người đăng ban đầu (không thay đổi khi bán/cho thuê)
  lister_id            INT             NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  lister_role          VARCHAR(20)     NOT NULL DEFAULT 'gym_owner', -- 'gym_owner' | 'member'
  category             gear_category   NOT NULL,
  name                 VARCHAR(200)    NOT NULL,
  description          TEXT,
  condition_rating     INT             NOT NULL CHECK (condition_rating BETWEEN 1 AND 5),
  condition_notes      TEXT,
  images               JSONB           NOT NULL DEFAULT '[]',
  listing_type         listing_type    NOT NULL DEFAULT 'rent',
  sell_price           DECIMAL(12,2)   CHECK (sell_price > 0),
  rent_price_day       DECIMAL(10,2)   CHECK (rent_price_day > 0),
  rent_price_week      DECIMAL(10,2)   CHECK (rent_price_week > 0),
  -- BR-13: deposit >= 50% sell_price (hoặc 50% * rent_price_day * 30)
  deposit_amount       DECIMAL(12,2)   CHECK (deposit_amount >= 0),
  qr_code_url          VARCHAR(500),
  verified             BOOLEAN         NOT NULL DEFAULT false,
  is_available         BOOLEAN         NOT NULL DEFAULT true,
  avg_rating           DECIMAL(2,1)    NOT NULL DEFAULT 0,
  total_reviews        INT             NOT NULL DEFAULT 0,
  created_at           TIMESTAMP       NOT NULL DEFAULT NOW(),
  -- BR-11B: member chỉ được đăng cho thuê (listing_type = 'rent')
  CONSTRAINT member_rent_only CHECK (
    lister_role <> 'member' OR listing_type = 'rent'
  )
);

CREATE INDEX idx_gear_owner    ON gear_items(current_owner_id);
CREATE INDEX idx_gear_category ON gear_items(category);
CREATE INDEX idx_gear_available ON gear_items(is_available);

-- ------------------------------------------------------------
-- 12. GEAR_LIFECYCLE — Lịch sử vòng đời thiết bị (Append-only)
-- ------------------------------------------------------------
CREATE TABLE gear_lifecycle (
  lifecycle_id     SERIAL          PRIMARY KEY,
  gear_id          VARCHAR(20)     NOT NULL REFERENCES gear_items(gear_id),
  owner_id         INT             NOT NULL REFERENCES users(user_id),
  action           lifecycle_action NOT NULL,
  condition_at_time INT            CHECK (condition_at_time BETWEEN 1 AND 5),
  notes            TEXT,
  photos           JSONB           DEFAULT '[]',
  -- Giá tại thời điểm: giá bán hoặc giá thuê
  price_snapshot   DECIMAL(12,2),
  timestamp        TIMESTAMP       NOT NULL DEFAULT NOW()
  -- BR-37: Append-only — KHÔNG được UPDATE/DELETE các bản ghi cũ
);

CREATE INDEX idx_lifecycle_gear ON gear_lifecycle(gear_id);

-- ------------------------------------------------------------
-- 13. GEAR_TRANSACTIONS — Giao dịch mua/thuê gear
-- ------------------------------------------------------------
CREATE TABLE gear_transactions (
  transaction_id   SERIAL          PRIMARY KEY,
  gear_id          VARCHAR(20)     NOT NULL REFERENCES gear_items(gear_id),
  seller_id        INT             NOT NULL REFERENCES users(user_id),
  buyer_id         INT             NOT NULL REFERENCES users(user_id),
  type             gear_txn_type   NOT NULL,
  amount           DECIMAL(12,2)   NOT NULL CHECK (amount > 0),
  deposit          DECIMAL(12,2)   NOT NULL DEFAULT 0,
  fitcoin_used     DECIMAL(12,2)   NOT NULL DEFAULT 0,
  rental_start     DATE,
  rental_end       DATE,
  status           gear_txn_status NOT NULL DEFAULT 'pending',
  created_at       TIMESTAMP       NOT NULL DEFAULT NOW(),
  CONSTRAINT rental_dates_required CHECK (
    type <> 'rental' OR (rental_start IS NOT NULL AND rental_end IS NOT NULL)
  ),
  CONSTRAINT valid_rental_dates CHECK (
    rental_end IS NULL OR rental_start IS NULL OR rental_end > rental_start
  )
);

CREATE INDEX idx_gear_txn_gear   ON gear_transactions(gear_id);
CREATE INDEX idx_gear_txn_seller ON gear_transactions(seller_id);
CREATE INDEX idx_gear_txn_buyer  ON gear_transactions(buyer_id);

-- ------------------------------------------------------------
-- 14. CHALLENGES — Thử thách weekly/monthly
-- ------------------------------------------------------------
CREATE TABLE challenges (
  challenge_id     SERIAL          PRIMARY KEY,
  title            VARCHAR(200)    NOT NULL,
  description      TEXT,
  type             challenge_type  NOT NULL,
  -- JSON: {"sessions_required": 5} hoặc {"total_volume": 10000}
  criteria         JSONB           NOT NULL,
  reward_xp        INT             NOT NULL CHECK (reward_xp > 0),
  reward_fitcoin   DECIMAL(10,2)   NOT NULL DEFAULT 0,
  start_date       DATE            NOT NULL,
  end_date         DATE            NOT NULL,
  is_active        BOOLEAN         NOT NULL DEFAULT true,
  CONSTRAINT valid_challenge_dates CHECK (end_date > start_date)
);

-- ------------------------------------------------------------
-- 15. USER_CHALLENGES — Tiến độ tham gia challenge
-- ------------------------------------------------------------
CREATE TABLE user_challenges (
  id               SERIAL          PRIMARY KEY,
  user_id          INT             NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  challenge_id     INT             NOT NULL REFERENCES challenges(challenge_id) ON DELETE CASCADE,
  progress         JSONB           DEFAULT '{}',
  status           user_challenge_status NOT NULL DEFAULT 'in_progress',
  completed_at     TIMESTAMP,
  UNIQUE (user_id, challenge_id)
);

CREATE INDEX idx_user_challenges_user ON user_challenges(user_id);

-- ------------------------------------------------------------
-- 16. BADGES — Danh sách huy hiệu trong hệ thống
-- ------------------------------------------------------------
CREATE TABLE badges (
  badge_id         SERIAL          PRIMARY KEY,
  name             VARCHAR(100)    NOT NULL UNIQUE,
  description      TEXT,
  icon_url         VARCHAR(500),
  -- JSON: {"total_sessions": 100} hoặc {"streak": 30}
  criteria         JSONB           NOT NULL,
  category         badge_category  NOT NULL
);

-- ------------------------------------------------------------
-- 17. FITCOIN_TRANSACTIONS — Lịch sử biến động FitCoin
-- ------------------------------------------------------------
CREATE TABLE fitcoin_transactions (
  txn_id           SERIAL          PRIMARY KEY,
  user_id          INT             NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  type             fitcoin_type    NOT NULL,
  amount           DECIMAL(12,2)   NOT NULL CHECK (amount > 0),
  source           fitcoin_source  NOT NULL,
  -- ID tham chiếu: order_id, challenge_id, gear_txn_id...
  reference_id     INT,
  balance_after    DECIMAL(12,2)   NOT NULL,
  note             TEXT,
  created_at       TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_fitcoin_user    ON fitcoin_transactions(user_id);
CREATE INDEX idx_fitcoin_created ON fitcoin_transactions(created_at DESC);

-- ------------------------------------------------------------
-- 18. SOCIAL_POSTS — Bài đăng trên Social Feed
-- ------------------------------------------------------------
CREATE TABLE social_posts (
  post_id          SERIAL          PRIMARY KEY,
  user_id          INT             NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  type             post_type       NOT NULL,
  content          TEXT,
  media_urls       JSONB           DEFAULT '[]',
  -- JSON: {"exercise": "Bench Press", "weight": 80, "reps": 5}
  linked_data      JSONB           DEFAULT '{}',
  likes_count      INT             NOT NULL DEFAULT 0,
  comments_count   INT             NOT NULL DEFAULT 0,
  created_at       TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_posts_user    ON social_posts(user_id);
CREATE INDEX idx_posts_created ON social_posts(created_at DESC);

-- ------------------------------------------------------------
-- 19. NOTIFICATIONS — Thông báo gửi đến user
-- ------------------------------------------------------------
CREATE TABLE notifications (
  notification_id  SERIAL          PRIMARY KEY,
  user_id          INT             NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  type             notif_type      NOT NULL,
  title            VARCHAR(200)    NOT NULL,
  message          TEXT,
  is_read          BOOLEAN         NOT NULL DEFAULT false,
  action_url       VARCHAR(500),
  created_at       TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notif_user_unread ON notifications(user_id, is_read);

-- ============================================================
-- BƯỚC 3: RULE BẢO VỆ GEAR_LIFECYCLE (Append-only)
-- Chặn UPDATE và DELETE theo BR-37
-- ============================================================

CREATE OR REPLACE FUNCTION prevent_lifecycle_mutation()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION
    'GEAR_LIFECYCLE là bảng append-only (BR-37). Không được phép UPDATE hoặc DELETE.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_lifecycle_no_update
  BEFORE UPDATE ON gear_lifecycle
  FOR EACH ROW EXECUTE FUNCTION prevent_lifecycle_mutation();

CREATE TRIGGER trg_lifecycle_no_delete
  BEFORE DELETE ON gear_lifecycle
  FOR EACH ROW EXECUTE FUNCTION prevent_lifecycle_mutation();

-- ============================================================
-- BƯỚC 4: HÀM TỰ ĐỘNG CẬP NHẬT FITCOIN KHI CÓ GIAO DỊCH
-- ============================================================

CREATE OR REPLACE FUNCTION update_fitcoin_balance()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.type IN ('earn', 'deposit', 'refund') THEN
    UPDATE users
    SET fitcoin_balance = fitcoin_balance + NEW.amount
    WHERE user_id = NEW.user_id;
  ELSIF NEW.type = 'spend' THEN
    IF (SELECT fitcoin_balance FROM users WHERE user_id = NEW.user_id) < NEW.amount THEN
      RAISE EXCEPTION 'Số dư FitCoin không đủ (BR-24).';
    END IF;
    UPDATE users
    SET fitcoin_balance = fitcoin_balance - NEW.amount
    WHERE user_id = NEW.user_id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_fitcoin_balance
  AFTER INSERT ON fitcoin_transactions
  FOR EACH ROW EXECUTE FUNCTION update_fitcoin_balance();

-- ============================================================
-- KẾT THÚC SCHEMA
-- ============================================================
