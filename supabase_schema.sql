-- ============================================================
-- RETAIL STORE MANAGEMENT — SUPABASE DATABASE SCHEMA
-- Run this entire file in your Supabase SQL Editor
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- PRODUCTS
CREATE TABLE IF NOT EXISTS products (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) DEFAULT 'General',
    sku VARCHAR(100) UNIQUE,
    stock_quantity INTEGER DEFAULT 0,
    cost_price DECIMAL(10,2) NOT NULL DEFAULT 0,
    selling_price DECIMAL(10,2) NOT NULL DEFAULT 0,
    low_stock_threshold INTEGER DEFAULT 10,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- SUPPLIERS
CREATE TABLE IF NOT EXISTS suppliers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    gst_number VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- PURCHASES (procurement)
CREATE TABLE IF NOT EXISTS purchases (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    supplier_id UUID REFERENCES suppliers(id) ON DELETE SET NULL,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    supplier_name VARCHAR(255) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    cost_price DECIMAL(10,2) NOT NULL,
    total_cost DECIMAL(10,2) GENERATED ALWAYS AS (quantity * cost_price) STORED,
    purchase_date DATE DEFAULT CURRENT_DATE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- SALES (invoices header)
CREATE TABLE IF NOT EXISTS sales (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(255) DEFAULT 'Walk-in Customer',
    subtotal DECIMAL(10,2) NOT NULL DEFAULT 0,
    discount DECIMAL(10,2) DEFAULT 0,
    tax DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'cash',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- SALE ITEMS (invoice lines)
CREATE TABLE IF NOT EXISTS sale_items (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    sale_id UUID REFERENCES sales(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);

-- AUTO updated_at
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = NOW(); RETURN NEW; END; $$ LANGUAGE plpgsql;
CREATE TRIGGER trg_products_updated BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- VIEWS
CREATE OR REPLACE VIEW low_stock_products AS
  SELECT id, name, category, stock_quantity, low_stock_threshold
  FROM products WHERE stock_quantity <= low_stock_threshold ORDER BY stock_quantity;

CREATE OR REPLACE VIEW product_sales_summary AS
  SELECT product_id, product_name,
    SUM(quantity) AS total_sold,
    SUM(total_price) AS total_revenue,
    COUNT(DISTINCT sale_id) AS num_orders
  FROM sale_items GROUP BY product_id, product_name ORDER BY total_sold DESC;

-- ROW LEVEL SECURITY
ALTER TABLE products   ENABLE ROW LEVEL SECURITY;
ALTER TABLE suppliers  ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchases  ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales      ENABLE ROW LEVEL SECURITY;
ALTER TABLE sale_items ENABLE ROW LEVEL SECURITY;

-- Allow all for authenticated users (adjust per role in production)
DO $$ BEGIN
  CREATE POLICY "auth_all_products"   ON products   FOR ALL TO authenticated USING (true) WITH CHECK (true);
  CREATE POLICY "auth_all_suppliers"  ON suppliers  FOR ALL TO authenticated USING (true) WITH CHECK (true);
  CREATE POLICY "auth_all_purchases"  ON purchases  FOR ALL TO authenticated USING (true) WITH CHECK (true);
  CREATE POLICY "auth_all_sales"      ON sales      FOR ALL TO authenticated USING (true) WITH CHECK (true);
  CREATE POLICY "auth_all_sale_items" ON sale_items FOR ALL TO authenticated USING (true) WITH CHECK (true);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- SAMPLE DATA
INSERT INTO products (name, category, sku, stock_quantity, cost_price, selling_price, low_stock_threshold) VALUES
  ('Basmati Rice 5kg',    'Groceries',     'GR-001', 150, 220.00, 299.00, 20),
  ('Tata Salt 1kg',       'Groceries',     'GR-002', 200,  18.00,  25.00, 30),
  ('Amul Butter 500g',    'Dairy',         'DA-001',  45, 240.00, 285.00, 15),
  ('Colgate Toothpaste',  'Personal Care', 'PC-001',   8,  55.00,  79.00, 10),
  ('Surf Excel 1kg',      'Household',     'HH-001',  60, 145.00, 185.00, 15),
  ('Maggi Noodles 70g',   'Instant Food',  'IF-001', 120,  12.00,  18.00, 25),
  ('Dettol Soap 125g',    'Personal Care', 'PC-002',   5,  38.00,  55.00, 10),
  ('Parle-G Biscuits',    'Snacks',        'SN-001', 200,   8.00,  12.00, 50),
  ('Haldiram Mixture',    'Snacks',        'SN-002',  30,  60.00,  85.00, 10),
  ('Aashirvaad Flour 5kg','Groceries',     'GR-003',  80, 195.00, 240.00, 15)
ON CONFLICT (sku) DO NOTHING;

INSERT INTO suppliers (name, contact_person, email, phone, address) VALUES
  ('Metro Cash & Carry', 'Rajesh Kumar', 'rajesh@metro.in',   '+91-98765-43210', 'Whitefield, Bengaluru'),
  ('Amul Dairy Ltd',     'Priya Sharma', 'priya@amul.coop',   '+91-98765-43211', 'Anand, Gujarat'),
  ('HUL Distributor',    'Anil Gupta',   'anil@hul-dist.com', '+91-98765-43212', 'Electronic City, Bengaluru');
