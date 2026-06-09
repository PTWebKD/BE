-- ============================================================
-- FitFuel+ Seed Extra — Thêm dữ liệu mẫu vào DB đang chạy
-- Chạy SAU seed.sql (hoặc khi DB đã có dữ liệu cũ)
-- Thêm: food_products #9-10, gear_items #10 (tổng 10 mỗi loại)
-- ============================================================

-- ------------------------------------------------------------
-- FOOD PRODUCTS: thêm sản phẩm 9 và 10
-- ------------------------------------------------------------
INSERT INTO food_products
  (product_id, vendor_id, name, description, price, calories,
   protein_g, carb_g, fat_g, ingredients, allergens, images,
   category, badge, is_available, avg_rating, total_reviews)
VALUES
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
  'High Protein', 'Mediterranean', true, 4.7, 87)

ON CONFLICT (product_id) DO NOTHING;

SELECT setval('food_products_product_id_seq', (SELECT MAX(product_id) FROM food_products));

-- ------------------------------------------------------------
-- GEAR ITEMS: thêm gear thứ 10
-- ------------------------------------------------------------
INSERT INTO gear_items
  (gear_id, current_owner_id, lister_id, lister_role, category, name, description,
   condition_rating, images, listing_type, sell_price, rent_price_day, rent_price_week,
   deposit_amount, verified, is_available, avg_rating, total_reviews)
VALUES
('GEAR-P5T1-0088', 6, 6, 'gym_owner', 'Cardio', 'Treadmill Pro X9 Commercial',
  'Máy chạy bộ thương mại 3.5HP, tốc độ 0.5-22 km/h, nghiêng 15 cấp, màn 10 inch, tải tối đa 180kg.',
  5,
  '["https://images.unsplash.com/photo-1571008887538-b36bb32f4571?w=600&h=400&fit=crop","https://images.unsplash.com/photo-1540497077202-7c8a3999166f?w=600&h=400&fit=crop"]',
  'both', 25000000, 300000, 1500000, 12500000, true, true, 4.9, 67)

ON CONFLICT (gear_id) DO NOTHING;

-- Lifecycle entry cho gear mới
INSERT INTO gear_lifecycle (gear_id, owner_id, action, condition_at_time, notes, price_snapshot)
VALUES ('GEAR-P5T1-0088', 6, 'listed', 5, 'Nhập máy chạy bộ thương mại mới 100%.', 25000000)
ON CONFLICT DO NOTHING;

-- ============================================================
-- KIỂM TRA
-- ============================================================
-- SELECT COUNT(*) FROM food_products;   -- phải = 10
-- SELECT COUNT(*) FROM gear_items;      -- phải = 10
