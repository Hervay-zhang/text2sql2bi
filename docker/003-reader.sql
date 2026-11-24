CREATE USER bi_reader WITH PASSWORD 'local_bi_reader_only';

GRANT CONNECT ON DATABASE text2sql2bi TO bi_reader;
GRANT USAGE ON SCHEMA public TO bi_reader;
GRANT SELECT ON customers, products, orders, order_items TO bi_reader;
