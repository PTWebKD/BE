-- ============================================================
-- FitFuel+ Seed Data
-- Dữ liệu mẫu khớp với mock data của Frontend
-- Chạy SAU schema.sql
-- ============================================================

-- ============================================================
-- 1. USERS (6 người dùng — khớp với mockUsers.js)
-- ============================================================
-- Mật khẩu: '123456' hash bằng bcrypt (cost 10)
-- Thực tế phải hash phía server, đây dùng placeholder

INSERT INTO users (user_id, email, phone, password_hash, role, display_name, avatar_url, fitness_goal, xp_total, current_level, current_streak, fitcoin_balance, tdee, created_at) VALUES
(1, 'alex@fitfuel.com',   '0901234561', '$2b$10$Alex.placeholder.hash.here.xxxxxxxxxxxxx', 'member',    'Alex Thunder', 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=150&h=150&fit=crop&crop=face', 'bulk',     4820, 8, 14, 2500.00, 2800, '2024-01-15 08:00:00'),
(2, 'sarah@fitfuel.com',  '0901234562', '$2b$10$Sarah.placeholder.hash.here.xxxxxxxxxxxx', 'member',    'Sarah Kim',    'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=150&h=150&fit=crop&crop=face', 'cut',      2310, 6, 7,  1200.00, 1900, '2024-03-22 09:00:00'),
(3, 'vendor@fitfuel.com', '0901234563', '$2b$10$Vendor.placeholder.hash.here.xxxxxxxxxxx', 'vendor',    'Mike Forge',   'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face', NULL,       0,    1, 0,  0.00,    NULL, '2024-02-01 10:00:00'),
(4, 'seller@fitfuel.com', '0901234564', '$2b$10$Seller.placeholder.hash.here.xxxxxxxxxxx', 'gym_owner', 'Tony Reps',    'https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?w=150&h=150&fit=crop&crop=face', 'maintain', 1500, 5, 0,  8000.00, 2500, '2024-01-01 08:00:00'),
(5, 'gym@fitfuel.com',    '0901234565', '$2b$10$Gym.placeholder.hash.here.xxxxxxxxxxxxx',  'gym_owner', 'Coach Dana',   'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face', 'maintain', 2000, 6, 5,  5000.00, 2600, '2024-01-05 08:00:00'),
(6, 'admin@fitfuel.com',  '0901234566', '$2b$10$Admin.placeholder.hash.here.xxxxxxxxxxx',  'gym_owner', 'Admin Rex',    'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face', 'bulk',     3000, 7, 2,  12000.00,2700, '2024-01-03 08:00:00');

SELECT setval('users_user_id_seq', 6);

-- ============================================================
-- 2. FITNESS_PASSPORT (chỉ cho member)
-- ============================================================
INSERT INTO fitness_passport (user_id, total_sessions, total_volume, longest_streak, body_weight_log, is_public) VALUES
(1, 127, 285000.00, 30,
  '[{"date":"2026-01-01","kg":82},{"date":"2026-02-01","kg":80},{"date":"2026-03-01","kg":79},{"date":"2026-04-01","kg":77},{"date":"2026-05-01","kg":76}]',
  true),
(2, 64, 142000.00, 14,
  '[{"date":"2026-01-01","kg":65},{"date":"2026-02-01","kg":63},{"date":"2026-03-01","kg":62},{"date":"2026-05-01","kg":60}]',
  true);

-- ============================================================
-- 3. GYMS (3 phòng tập)
-- ============================================================
INSERT INTO gyms (gym_id, owner_id, name, address, phone, opening_hours, services, membership_plans) VALUES
(1, 4, 'Iron Gear Co. Gym',
  '123 Võ Văn Tần, Quận 3, TP.HCM', '02838123456',
  '{"mon_fri": "05:30-22:30", "sat": "06:00-22:00", "sun": "07:00-20:00"}',
  '["gym", "powerlifting", "gear_hub"]',
  '[{"name":"Gói Tháng","price":500000},{"name":"Gói Năm","price":5000000}]'),

(2, 5, 'Apex Performance Gym',
  '456 Lê Lợi, Quận 1, TP.HCM', '02839234567',
  '{"mon_fri": "05:00-23:00", "sat": "06:00-22:00", "sun": "07:00-21:00"}',
  '["gym", "yoga", "boxing", "pt_session"]',
  '[{"name":"Gói Tháng","price":600000},{"name":"Gói Năm","price":6000000}]'),

(3, 6, 'Rex Power Gym',
  '789 Nguyễn Huệ, Quận 1, TP.HCM', '02840345678',
  '{"mon_fri": "05:00-23:30", "sat": "06:00-23:00", "sun": "06:00-22:00"}',
  '["gym", "crossfit", "swimming", "sauna"]',
  '[{"name":"Gói Tháng","price":550000},{"name":"Gói Năm","price":5500000}]');

SELECT setval('gyms_gym_id_seq', 3);

-- ============================================================
-- 4. GYM_MEMBERSHIPS
-- ============================================================
INSERT INTO gym_memberships (user_id, gym_id, plan_name, start_date, end_date, status, auto_renew, payment_method, amount_paid) VALUES
(1, 1, 'Gói Tháng', '2026-05-01', '2026-05-31', 'active',  false, 'vnpay', 500000),
(2, 2, 'Gói Tháng', '2026-05-01', '2026-05-31', 'active',  false, 'momo',  600000),
(1, 2, 'Gói Năm',   '2026-01-01', '2026-12-31', 'active',  true,  'vnpay', 6000000);

-- ============================================================
-- 5. FOLLOWS
-- ============================================================
INSERT INTO follows (follower_id, following_id) VALUES
(1, 2), (1, 4), (1, 5),
(2, 1), (2, 5),
(4, 1), (5, 1), (5, 2);

-- ============================================================
-- 6. WORKOUT_SESSIONS
-- ============================================================
INSERT INTO workout_sessions (session_id, user_id, gym_id, date, duration_min, status, notes) VALUES
(1, 1, 1, '2026-05-08', 75, 'done',   'Ngày chân — squat PR mới'),
(2, 1, 1, '2026-05-09', 60, 'done',   'Ngực + vai'),
(3, 1, 1, '2026-05-10', 80, 'done',   'Lưng nặng'),
(4, 1, 1, '2026-05-12', 70, 'done',   'Tay + core'),
(5, 2, 2, '2026-05-09', 55, 'done',   'Full body nhẹ'),
(6, 2, 2, '2026-05-11', 65, 'done',   'HIIT + cardio'),
(7, 1, 1, '2026-05-13', 50, 'active', NULL);

SELECT setval('workout_sessions_session_id_seq', 7);

-- ============================================================
-- 7. EXERCISE_LOGS
-- ============================================================
INSERT INTO exercise_logs (session_id, exercise_name, muscle_group, sets, is_pr, notes) VALUES
-- Session 1 (ngày chân)
(1, 'Squat',            'legs',      '[{"reps":5,"weight":120},{"reps":5,"weight":125},{"reps":3,"weight":130}]', true,  'PR mới 130kg'),
(1, 'Romanian Deadlift','legs',      '[{"reps":10,"weight":90},{"reps":10,"weight":90},{"reps":10,"weight":90}]', false, NULL),
(1, 'Leg Press',        'legs',      '[{"reps":12,"weight":200},{"reps":12,"weight":220},{"reps":10,"weight":240}]', false, NULL),
-- Session 2 (ngực + vai)
(2, 'Bench Press',      'chest',     '[{"reps":5,"weight":100},{"reps":5,"weight":105},{"reps":4,"weight":107.5}]', true, 'PR mới 107.5kg'),
(2, 'Incline DB Press', 'chest',     '[{"reps":10,"weight":40},{"reps":10,"weight":40},{"reps":8,"weight":42}]', false, NULL),
(2, 'OHP',              'shoulders', '[{"reps":8,"weight":65},{"reps":8,"weight":65},{"reps":6,"weight":70}]', false, NULL),
-- Session 3 (lưng)
(3, 'Deadlift',         'back',      '[{"reps":5,"weight":150},{"reps":3,"weight":160},{"reps":1,"weight":170}]', true, 'All-time PR 170kg'),
(3, 'Pull-up',          'back',      '[{"reps":10,"weight":0},{"reps":9,"weight":0},{"reps":8,"weight":0}]', false, NULL),
(3, 'Barbell Row',      'back',      '[{"reps":8,"weight":80},{"reps":8,"weight":82.5},{"reps":8,"weight":82.5}]', false, NULL),
-- Session 5 (Sarah)
(5, 'Squat',            'legs',      '[{"reps":10,"weight":50},{"reps":10,"weight":55},{"reps":8,"weight":57.5}]', false, NULL),
(5, 'Bench Press',      'chest',     '[{"reps":10,"weight":40},{"reps":10,"weight":42},{"reps":8,"weight":45}]', true, 'PR mới'),
(5, 'Plank',            'core',      '[{"reps":60,"weight":0},{"reps":60,"weight":0},{"reps":45,"weight":0}]', false, 'reps = giây');

-- ============================================================
-- 8. FOOD_PRODUCTS (khớp với mockFood.js — vendor_id = 3)
-- ============================================================
INSERT INTO food_products (product_id, vendor_id, name, description, price, calories, protein_g, carb_g, fat_g, ingredients, allergens, images, category, badge, is_available, avg_rating, total_reviews) VALUES
(1, 3, 'Power Protein Bowl',
  'Ức gà nướng, quinoa, khoai lang nướng, bơ và rau xanh với sốt tahini chanh.',
  89000, 520, 45.0, 38.0, 12.0,
  '["uc ga","quinoa","khoai lang","bo","rau xanh","sot tahini"]',
  '["gluten"]',
  '["https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&h=400&fit=crop"]',
  'High Protein', 'Best Seller', true, 4.9, 234),

(2, 3, 'Keto Warrior Plate',
  'Thịt bò ăn cỏ, bắp cải nghiền sốt bơ, rau bina xào, thịt bacon giòn.',
  95000, 480, 38.0, 8.0, 34.0,
  '["thit bo","canh hoa","rau bina","bacon","bo"]',
  '[]',
  '["https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&h=400&fit=crop"]',
  'Keto', 'Keto Friendly', true, 4.7, 178),

(3, 3, 'Vegan Gains Bowl',
  'Tempeh, đậu đen, gạo lứt, xoài salsa và sốt chanh rau mùi.',
  79000, 440, 28.0, 55.0, 14.0,
  '["tempeh","dau den","gao lut","xoai","rau mui"]',
  '[]',
  '["https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=600&h=400&fit=crop"]',
  'Vegan', 'Vegan', true, 4.6, 143),

(4, 3, 'Bulk King Meal',
  'Đôi ức gà, 2 chén cơm, khoai lang, bông cải xanh và sốt protein.',
  115000, 950, 72.0, 95.0, 28.0,
  '["uc ga","com trang","khoai lang","bong cai xanh","sot protein"]',
  '[]',
  '["https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&h=400&fit=crop"]',
  'Bulk', 'Bulk Special', true, 4.8, 312),

(5, 3, 'Shred Mode Salad',
  'Cá ngừ, rau hỗn hợp, cà chua bi, dưa leo, trứng và giấm táo.',
  72000, 280, 32.0, 18.0, 9.0,
  '["ca ngu","rau mix","ca chua bi","dua leo","trung","giam tao"]',
  '[]',
  '["https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&h=400&fit=crop"]',
  'Cut', 'Shred Pick', true, 4.5, 97),

(6, 3, 'Pre-Workout Fuel',
  'Chuối yến mạch, mật ong, bơ đậu phộng, hạt chia và chà là.',
  65000, 380, 18.0, 62.0, 6.0,
  '["chuoi","yen mach","mat ong","bu dau phong","hat chia","cha la"]',
  '["gluten"]',
  '["https://images.unsplash.com/photo-1547592180-85f173990554?w=600&h=400&fit=crop"]',
  'Pre-Workout', 'Energy Boost', true, 4.7, 204),

(7, 3, 'Recovery Smoothie Bowl',
  'Açaí, chuối, bột protein, granola, quả mọng và dừa bào.',
  68000, 320, 24.0, 48.0, 7.0,
  '["acai","chuoi","bot protein","granola","qua mong","dua bao"]',
  '[]',
  '["https://images.unsplash.com/photo-1490474418585-ba9bad8fd0ea?w=600&h=400&fit=crop"]',
  'Recovery', 'Recovery+', true, 4.8, 156),

(8, 3, 'Salmon Power Pack',
  'Cá hồi tự nhiên, măng tây nướng, gạo lứt và sốt thì là chanh.',
  125000, 560, 48.0, 32.0, 24.0,
  '["ca hoi","mang tay","gao lut","thi la","chanh"]',
  '[]',
  '["https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=600&h=400&fit=crop","https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=600&h=400&fit=crop"]',
  'High Protein', 'Premium', false, 4.9, 89),

(9, 3, 'Thai Basil Chicken Bowl',
  'Gà xào húng quế Thái, cơm hoa lài, trứng ốp la, ớt chuông và nước mắm pha.',
  85000, 490, 40.0, 44.0, 14.0,
  '["ga","hung que","com hoa lai","trung","ot chuong","nuoc mam"]',
  '["gluten"]',
  '["https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600&h=400&fit=crop","https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&h=400&fit=crop"]',
  'High Protein', 'Asian Pick', true, 4.6, 118),

(10, 3, 'Mediterranean Power Wrap',
  'Gà nướng, phô mai feta, dưa leo, cà chua, rau bina, sốt tzatziki cuộn bánh mì nguyên cám.',
  92000, 420, 36.0, 34.0, 16.0,
  '["ga nuong","pho mai feta","dua leo","ca chua","rau bina","sot tzatziki","banh mi nguyen cam"]',
  '["gluten","dairy"]',
  '["https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=600&h=400&fit=crop","https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=600&h=400&fit=crop"]',
  'High Protein', 'Mediterranean', true, 4.7, 87);

SELECT setval('food_products_product_id_seq', 10);

-- ============================================================
-- 9. FOOD_ORDERS
-- ============================================================
INSERT INTO food_orders (order_id, user_id, guest_phone, vendor_id, items, subtotal, delivery_fee, total_amount, fitcoin_used, delivery_address, delivery_time, status, payment_method) VALUES
(1, 1, NULL, 3,
  '[{"product_id":1,"qty":1,"price":89000,"name":"Power Protein Bowl"},{"product_id":6,"qty":1,"price":65000,"name":"Pre-Workout Fuel"}]',
  154000, 15000, 169000, 0, '123 Võ Văn Tần, Q3, HCM', '12:00-12:30', 'delivered', 'vnpay'),

(2, 2, NULL, 3,
  '[{"product_id":5,"qty":1,"price":72000,"name":"Shred Mode Salad"},{"product_id":7,"qty":1,"price":68000,"name":"Recovery Smoothie Bowl"}]',
  140000, 15000, 155000, 20000, '456 Lê Lợi, Q1, HCM', '13:00-13:30', 'delivered', 'fitcoin'),

(3, 1, NULL, 3,
  '[{"product_id":4,"qty":2,"price":115000,"name":"Bulk King Meal"}]',
  230000, 25000, 255000, 0, '123 Võ Văn Tần, Q3, HCM', '18:00-18:30', 'preparing', 'momo'),

(4, NULL, '0912345678', 3,
  '[{"product_id":2,"qty":1,"price":95000,"name":"Keto Warrior Plate"}]',
  95000, 15000, 110000, 0, '789 Nguyễn Huệ, Q1, HCM', '11:00-11:30', 'confirmed', 'cash');

SELECT setval('food_orders_order_id_seq', 4);

-- ============================================================
-- 10. FOOD_REVIEWS
-- ============================================================
INSERT INTO food_reviews (product_id, user_id, rating, comment, helpful_votes) VALUES
(1, 1, 5, 'Protein cao, ngon, đóng gói cẩn thận. Sẽ order lại!', 8),
(1, 2, 5, 'Rất tươi và đầy đủ dinh dưỡng.', 3),
(4, 1, 5, 'Đúng chuẩn bữa bulk — ăn xong cảm giác mạnh mẽ hẳn.', 5),
(5, 2, 4, 'Ngon nhưng hơi ít. Phù hợp với người đang cut.', 2),
(7, 2, 5, 'Phục hồi sau tập rất tốt, vị cũng ổn.', 4);

-- ============================================================
-- 11. GEAR_ITEMS (khớp với mockGear.js)
-- ============================================================
INSERT INTO gear_items (gear_id, current_owner_id, lister_id, lister_role, category, name, description, condition_rating, images, listing_type, sell_price, rent_price_day, rent_price_week, deposit_amount, verified, is_available, avg_rating, total_reviews) VALUES
('GEAR-K7X2-3841', 4, 4, 'gym_owner', 'Weights', 'Titan Barbell Pro 20kg',
  'Thanh đòn Olympic tiêu chuẩn thi đấu. Thép mạ chrome 20kg, 2 vạch knurl. Tối đa 680kg.',
  5, '["https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=600&h=400&fit=crop","https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=600&h=400&fit=crop"]',
  'both', 2800000, 56000, 280000, 1400000, true, true, 4.9, 456),

('GEAR-A2P4-1222', 4, 4, 'gym_owner', 'Apparel', 'Alpha Performance Tee',
  'Áo thể thao co giãn 4 chiều, kháng khuẩn, phù hợp tập nặng.',
  4, '["https://images.unsplash.com/photo-1539185441755-769473a23570?w=600&h=400&fit=crop"]',
  'sell', 380000, NULL, NULL, NULL, true, true, 4.7, 312),

('GEAR-W9Q1-5033', 4, 4, 'gym_owner', 'Supplements', 'Whey Isolate 2kg',
  'Whey isolate lọc vi siêu. 27g protein/serving, <1g lactose. Vị Chocolate Fudge.',
  5, '["https://images.unsplash.com/photo-1593095948071-474c5cc2989d?w=600&h=400&fit=crop"]',
  'sell', 950000, NULL, NULL, NULL, true, true, 4.8, 789),

('GEAR-D5M3-8814', 4, 4, 'gym_owner', 'Weights', 'Adjustable Dumbbell Set 5-52.5kg',
  'Thay thế 15 bộ tạ. Cơ chế chọn số, thép đúc. Bán theo cặp.',
  5, '["https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&h=400&fit=crop"]',
  'both', 4500000, 90000, 450000, 2250000, true, true, 4.9, 234),

('GEAR-B8R6-2291', 4, 4, 'gym_owner', 'Accessories', 'Resistance Bands Pro Kit',
  'Bộ 5 dây kháng lực 10-200 lbs. Cao su tự nhiên, dây an toàn, túi đựng.',
  4, '["https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=600&h=400&fit=crop"]',
  'both', 280000, 5600, 28000, 140000, true, true, 4.6, 567),

('GEAR-C1T9-7742', 5, 5, 'gym_owner', 'Cardio', 'Air Assault Bike Pro',
  'Xe đạp kháng lực không khí toàn thân. Màn LCD, tay nắm đo nhịp tim.',
  5, '["https://images.unsplash.com/photo-1540497077202-7c8a3999166f?w=600&h=400&fit=crop"]',
  'both', 12500000, 250000, 1250000, 6250000, true, true, 4.8, 123),

('GEAR-G3N7-4455', 5, 5, 'gym_owner', 'Recovery', 'Massage Gun Pro X3',
  'Thiết bị massage percussive 30 tốc độ. 6 đầu, 3200 RPM, pin 8 giờ.',
  4, '["https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=600&h=400&fit=crop"]',
  'both', 1200000, 24000, 120000, 600000, false, true, 4.7, 398),

('GEAR-L2K8-9963', 4, 4, 'gym_owner', 'Accessories', 'Lifting Belt 10mm',
  'Đai tập powerlifting chuẩn IPF. Da thật 10mm, khóa đơn, lưng 4 inch.',
  5, '["https://images.unsplash.com/photo-1526506118085-60ce8714f8c5?w=600&h=400&fit=crop"]',
  'both', 650000, 13000, 65000, 325000, true, true, 4.8, 211),

('GEAR-P5T1-0088', 6, 6, 'gym_owner', 'Cardio', 'Treadmill Pro X9 Commercial',
  'Máy chạy bộ thương mại 3.5HP, tốc độ 0.5-22 km/h, nghiêng 15 cấp, màn 10 inch, max 180kg.',
  5, '["https://images.unsplash.com/photo-1571008887538-b36bb32f4571?w=600&h=400&fit=crop","https://images.unsplash.com/photo-1540497077202-7c8a3999166f?w=600&h=400&fit=crop"]',
  'both', 25000000, 300000, 1500000, 12500000, true, true, 4.9, 67),

-- Gear đăng bởi Member (chỉ cho thuê — BR-11B)
('GEAR-M1X5-3377', 1, 1, 'member', 'Accessories', 'Dây kháng lực cá nhân',
  'Bộ dây kháng lực dùng 3 tháng còn mới. Phù hợp tập tại nhà.',
  4, '["https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=600&h=400&fit=crop"]',
  'rent', NULL, 15000, 75000, 90000, false, true, 0.0, 0);

-- ============================================================
-- 12. GEAR_LIFECYCLE (lịch sử vòng đời)
-- ============================================================
INSERT INTO gear_lifecycle (gear_id, owner_id, action, condition_at_time, notes, price_snapshot) VALUES
('GEAR-K7X2-3841', 4, 'listed',   5, 'Nhập từ nhà sản xuất, mới 100%.', 2800000),
('GEAR-K7X2-3841', 1, 'rented',   5, 'Thuê 7 ngày để chuẩn bị thi đấu.', 280000),
('GEAR-K7X2-3841', 4, 'returned', 4, 'Trả đúng hạn, có vài vết xước nhỏ.', NULL),

('GEAR-D5M3-8814', 4, 'listed',   5, 'Mới 100%, còn nguyên hộp.', 4500000),
('GEAR-D5M3-8814', 2, 'rented',   5, 'Thuê 14 ngày.', 900000),
('GEAR-D5M3-8814', 4, 'returned', 5, 'Trả đúng hạn, tình trạng tốt.', NULL),

('GEAR-C1T9-7742', 5, 'listed',   5, 'Mua từ nhà phân phối chính hãng.', 12500000),

('GEAR-G3N7-4455', 5, 'listed',   4, 'Đã dùng 6 tháng, còn hoạt động tốt.', 1200000),

('GEAR-M1X5-3377', 1, 'listed',   4, 'Dùng 3 tháng, muốn cho thuê lại.', NULL);

-- ============================================================
-- 13. GEAR_TRANSACTIONS
-- ============================================================
INSERT INTO gear_transactions (gear_id, seller_id, buyer_id, type, amount, deposit, fitcoin_used, rental_start, rental_end, status) VALUES
('GEAR-K7X2-3841', 4, 1, 'rental', 280000, 1400000, 0, '2026-04-10', '2026-04-17', 'completed'),
('GEAR-D5M3-8814', 4, 2, 'rental', 900000, 2250000, 0, '2026-04-15', '2026-04-29', 'completed'),
('GEAR-B8R6-2291', 4, 2, 'sale',   280000, 0,       0, NULL,         NULL,         'completed');

-- ============================================================
-- 14. CHALLENGES
-- ============================================================
INSERT INTO challenges (challenge_id, title, description, type, criteria, reward_xp, reward_fitcoin, start_date, end_date, is_active) VALUES
(1, 'Tuần Chiến Binh',
  'Hoàn thành 5 buổi tập trong tuần này.',
  'weekly',
  '{"sessions_required": 5}',
  100, 50.00, '2026-05-06', '2026-05-12', false),

(2, 'Tháng Bền Bỉ',
  'Đạt streak 20 ngày liên tiếp trong tháng.',
  'monthly',
  '{"streak_required": 20}',
  200, 150.00, '2026-05-01', '2026-05-31', true),

(3, 'Protein Warrior',
  'Đặt 10 đơn hàng High Protein trong tháng.',
  'monthly',
  '{"protein_orders": 10}',
  150, 100.00, '2026-05-01', '2026-05-31', true),

(4, 'Tuần Hàng Đầu',
  'Hoàn thành 5 buổi tập tuần này và đặt ít nhất 3 đơn food.',
  'weekly',
  '{"sessions_required": 5, "food_orders": 3}',
  150, 75.00, '2026-05-13', '2026-05-19', true);

SELECT setval('challenges_challenge_id_seq', 4);

-- ============================================================
-- 15. USER_CHALLENGES
-- ============================================================
INSERT INTO user_challenges (user_id, challenge_id, progress, status, completed_at) VALUES
(1, 1, '{"sessions_done": 5}', 'completed', '2026-05-11 18:00:00'),
(2, 1, '{"sessions_done": 3}', 'failed',    NULL),
(1, 2, '{"current_streak": 14}', 'in_progress', NULL),
(2, 2, '{"current_streak": 7}',  'in_progress', NULL),
(1, 4, '{"sessions_done": 4, "food_orders": 2}', 'in_progress', NULL);

-- ============================================================
-- 16. BADGES
-- ============================================================
INSERT INTO badges (badge_id, name, description, icon_url, criteria, category) VALUES
(1,  'Iron Newbie',       'Hoàn thành buổi tập đầu tiên.',           NULL, '{"total_sessions": 1}',   'gym'),
(2,  'Century Club',      'Hoàn thành 100 buổi tập.',                 NULL, '{"total_sessions": 100}', 'gym'),
(3,  'PR Breaker',        'Phá 5 kỷ lục cá nhân.',                   NULL, '{"total_prs": 5}',        'gym'),
(4,  'Streak 7',          'Duy trì streak 7 ngày.',                   NULL, '{"streak": 7}',           'streak'),
(5,  'Streak 30',         'Duy trì streak 30 ngày.',                  NULL, '{"streak": 30}',          'streak'),
(6,  'Streak 100',        'Duy trì streak 100 ngày.',                 NULL, '{"streak": 100}',         'streak'),
(7,  'Foodie Fighter',    'Đặt 20 đơn healthy food.',                 NULL, '{"food_orders": 20}',     'food'),
(8,  'Gear Collector',    'Hoàn thành 3 giao dịch thuê gear.',        NULL, '{"gear_rentals": 3}',     'gear'),
(9,  'Social Butterfly',  'Được 50 người follow.',                    NULL, '{"followers": 50}',       'social'),
(10, 'Legend',            'Đạt Level 10 trong hệ thống.',             NULL, '{"level": 10}',           'gym');

SELECT setval('badges_badge_id_seq', 10);

-- ============================================================
-- 17. FITCOIN_TRANSACTIONS
-- Disable trigger tạm thời vì balance đã được set đúng trong bảng users
-- ============================================================
ALTER TABLE fitcoin_transactions DISABLE TRIGGER trg_fitcoin_balance;

INSERT INTO fitcoin_transactions (user_id, type, amount, source, reference_id, balance_after, note) VALUES
-- Alex earn
(1, 'earn',  100.00, 'challenge',   1,    100.00,  'Hoàn thành Tuần Chiến Binh'),
(1, 'earn',  50.00,  'streak',      NULL, 150.00,  'Streak milestone 7 ngày'),
(1, 'earn',  80.00,  'gear_sale',   1,    230.00,  'Cho thuê GEAR-K7X2-3841'),
(1, 'earn', 2000.00, 'deposit',     NULL, 2230.00, 'Nạp FitCoin'),
(1, 'spend', 300.00, 'food_order',  2,    1930.00, 'Mua Power Protein Bowl'),
-- Sarah earn
(2, 'earn',   50.00, 'referral',    NULL, 50.00,   'Giới thiệu bạn thành công'),
(2, 'spend',  50.00, 'food_order',  2,    0.00,    'Dùng FitCoin mua food'),
(2, 'earn', 1200.00, 'deposit',     NULL, 1200.00, 'Nạp FitCoin'),
-- Tony earn từ cho thuê
(4, 'earn',  238000.00,'gear_rental',1,   238000.00,'Thu từ cho thuê GEAR-K7X2-3841 (trừ 15% hoa hồng)');

ALTER TABLE fitcoin_transactions ENABLE TRIGGER trg_fitcoin_balance;

-- ============================================================
-- 18. SOCIAL_POSTS
-- ============================================================
INSERT INTO social_posts (user_id, type, content, linked_data, likes_count, comments_count) VALUES
(1, 'pr',
  '🏋️ Vừa phá PR Deadlift 170kg! 3 tháng kiên trì cuối cùng cũng đến ngày này!',
  '{"exercise": "Deadlift", "weight": 170, "reps": 1, "previous_pr": 160}',
  42, 8),

(1, 'streak',
  '🔥 Streak 14 ngày liên tiếp! Không có gì có thể ngăn tôi lại!',
  '{"streak_days": 14}',
  28, 5),

(2, 'pr',
  '💪 PR Bench Press mới: 45kg! Đang tiến bộ từng ngày!',
  '{"exercise": "Bench Press", "weight": 45, "reps": 5}',
  19, 3),

(1, 'milestone',
  '🎯 Vừa hoàn thành thử thách Tuần Chiến Binh — 5 buổi tập trong 1 tuần!',
  '{"challenge": "Tuần Chiến Binh", "reward_xp": 100}',
  15, 2);

-- ============================================================
-- 19. NOTIFICATIONS
-- ============================================================
INSERT INTO notifications (user_id, type, title, message, is_read, action_url) VALUES
(1, 'order_update',    'Đơn hàng đã giao',      'Đơn #3 (Bulk King Meal x2) đang được chuẩn bị.', false, '/orders/3'),
(1, 'challenge',       'Thử thách mới!',         'Tuần Hàng Đầu bắt đầu từ hôm nay — nhận 150 XP!', false, '/challenges'),
(1, 'streak_reminder', 'Nhớ tập hôm nay!',       'Đừng để mất streak 14 ngày của bạn!', true, '/gym/new-session'),
(2, 'order_update',    'Đơn hàng đã giao',       'Đơn #2 (Shred Mode + Recovery Bowl) đã giao thành công.', true, '/orders/2'),
(2, 'challenge',       'Tham gia thử thách!',    'Tháng Bền Bỉ đang diễn ra — bạn còn 17 ngày để đạt streak 20!', false, '/challenges'),
(1, 'gear_return',     'Nhắc nhở trả gear',      'Gear GEAR-K7X2-3841 đã đến hạn trả ngày mai.', true, '/orders'),
(4, 'gear_approved',   'Gear đã được duyệt',     'Listing GEAR-L2K8-9963 (Lifting Belt) đã được duyệt và hiển thị.', true, '/gear/manage');

-- ============================================================
-- KIỂM TRA DỮ LIỆU SAU KHI SEED
-- ============================================================

-- Chạy các câu query sau để xác nhận:
-- SELECT role, COUNT(*) FROM users GROUP BY role;
-- SELECT COUNT(*) FROM food_products;
-- SELECT COUNT(*) FROM gear_items;
-- SELECT COUNT(*) FROM gear_lifecycle;
-- SELECT lister_role, listing_type, COUNT(*) FROM gear_items GROUP BY lister_role, listing_type;

-- ============================================================
-- KẾT THÚC SEED
-- ============================================================
