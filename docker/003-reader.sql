CREATE USER bi_reader WITH PASSWORD 'bi_reader_password';

GRANT CONNECT ON DATABASE text2sql2bi TO bi_reader;
GRANT USAGE ON SCHEMA public TO bi_reader;
GRANT SELECT ON customers, products, orders, order_items TO bi_reader;
