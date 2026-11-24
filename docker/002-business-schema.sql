CREATE TABLE customers (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  region TEXT NOT NULL,
  segment TEXT NOT NULL,
  created_at DATE NOT NULL
);

CREATE TABLE products (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  unit_price NUMERIC(12, 2) NOT NULL
);

CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,
  customer_id BIGINT NOT NULL REFERENCES customers(id),
  order_date DATE NOT NULL,
  status TEXT NOT NULL,
  channel TEXT NOT NULL
);

CREATE TABLE order_items (
  id BIGSERIAL PRIMARY KEY,
  order_id BIGINT NOT NULL REFERENCES orders(id),
  product_id BIGINT NOT NULL REFERENCES products(id),
  quantity INTEGER NOT NULL,
  unit_price NUMERIC(12, 2) NOT NULL
);

INSERT INTO customers (name, region, segment, created_at) VALUES
('远山科技', '华东', '企业', '2025-01-12'),
('新禾商贸', '华南', '中小企业', '2025-02-03'),
('北辰零售', '华北', '零售', '2025-02-18'),
('江海制造', '华东', '企业', '2025-03-11'),
('西岭文化', '西南', '中小企业', '2025-04-02'),
('云帆教育', '华南', '企业', '2025-04-26');

INSERT INTO products (name, category, unit_price) VALUES
('数据分析专业版', '软件订阅', 1299),
('智能报表套件', '软件订阅', 899),
('实施服务包', '专业服务', 5000),
('数据治理咨询', '专业服务', 8000),
('API调用包', '增值服务', 499);

INSERT INTO orders (customer_id, order_date, status, channel) VALUES
(1, '2026-01-08', 'paid', '直销'),
(2, '2026-01-19', 'paid', '线上'),
(3, '2026-02-05', 'paid', '渠道'),
(1, '2026-02-16', 'paid', '直销'),
(4, '2026-03-03', 'paid', '直销'),
(5, '2026-03-22', 'cancelled', '线上'),
(6, '2026-04-09', 'paid', '渠道'),
(2, '2026-04-21', 'paid', '线上'),
(4, '2026-05-12', 'paid', '直销'),
(3, '2026-05-25', 'paid', '渠道'),
(1, '2026-06-07', 'paid', '直销'),
(6, '2026-06-18', 'paid', '线上');

INSERT INTO order_items (
  order_id,
  product_id,
  quantity,
  unit_price
) VALUES
(1, 1, 10, 1199),
(1, 3, 1, 5000),
(2, 2, 5, 849),
(3, 5, 20, 459),
(4, 4, 1, 8000),
(5, 1, 20, 1099),
(5, 3, 2, 4800),
(6, 2, 3, 899),
(7, 1, 15, 1149),
(7, 5, 30, 449),
(8, 2, 8, 829),
(9, 4, 2, 7600),
(10, 5, 40, 439),
(11, 1, 25, 1049),
(12, 2, 12, 799);

