SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS clinic_pharmacy
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE clinic_pharmacy;

CREATE TABLE IF NOT EXISTS users (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(64) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  nickname VARCHAR(64) NOT NULL,
  role VARCHAR(32) NOT NULL,
  phone VARCHAR(32) DEFAULT NULL,
  email VARCHAR(128) DEFAULT NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'enabled',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS suppliers (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(128) NOT NULL UNIQUE,
  contact_person VARCHAR(64) NOT NULL,
  phone VARCHAR(32) NOT NULL,
  email VARCHAR(128) DEFAULT NULL,
  address VARCHAR(255) NOT NULL,
  supply_scope VARCHAR(255) NOT NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'active',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS medicines (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  code VARCHAR(64) NOT NULL UNIQUE,
  name VARCHAR(128) NOT NULL,
  specification VARCHAR(128) NOT NULL,
  unit VARCHAR(32) NOT NULL,
  category VARCHAR(64) NOT NULL,
  current_stock INT NOT NULL DEFAULT 0,
  safety_stock INT NOT NULL DEFAULT 0,
  selling_price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  purchase_price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  expiry_warning_days INT NOT NULL DEFAULT 90,
  supplier_id BIGINT DEFAULT NULL,
  location VARCHAR(128) DEFAULT NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'active',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_medicines_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS medicine_batches (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  medicine_id BIGINT NOT NULL,
  supplier_id BIGINT DEFAULT NULL,
  batch_no VARCHAR(64) NOT NULL,
  inbound_order_no VARCHAR(64) NOT NULL,
  quantity INT NOT NULL,
  remaining_quantity INT NOT NULL,
  production_date DATE DEFAULT NULL,
  expiry_date DATE NOT NULL,
  inbound_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  location VARCHAR(128) DEFAULT NULL,
  remark VARCHAR(255) DEFAULT NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'available',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_batches_medicine FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE,
  CONSTRAINT fk_batches_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS inbound_orders (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  order_no VARCHAR(64) NOT NULL UNIQUE,
  medicine_id BIGINT NOT NULL,
  supplier_id BIGINT DEFAULT NULL,
  batch_id BIGINT DEFAULT NULL,
  batch_no VARCHAR(64) NOT NULL,
  quantity INT NOT NULL,
  purchase_price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  received_by VARCHAR(64) NOT NULL,
  received_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(16) NOT NULL DEFAULT 'completed',
  remark VARCHAR(255) DEFAULT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_inbound_medicine FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE RESTRICT,
  CONSTRAINT fk_inbound_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL,
  CONSTRAINT fk_inbound_batch FOREIGN KEY (batch_id) REFERENCES medicine_batches(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS prescription_issues (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  issue_no VARCHAR(64) NOT NULL UNIQUE,
  patient_name VARCHAR(64) NOT NULL,
  doctor_name VARCHAR(64) NOT NULL,
  issued_by BIGINT NOT NULL,
  issued_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  status VARCHAR(16) NOT NULL DEFAULT 'completed',
  remark VARCHAR(255) DEFAULT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_prescription_user FOREIGN KEY (issued_by) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS prescription_issue_items (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  issue_id BIGINT NOT NULL,
  medicine_id BIGINT NOT NULL,
  batch_id BIGINT DEFAULT NULL,
  quantity INT NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_issue_items_issue FOREIGN KEY (issue_id) REFERENCES prescription_issues(id) ON DELETE CASCADE,
  CONSTRAINT fk_issue_items_medicine FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE RESTRICT,
  CONSTRAINT fk_issue_items_batch FOREIGN KEY (batch_id) REFERENCES medicine_batches(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS stock_counts (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  count_no VARCHAR(64) NOT NULL UNIQUE,
  medicine_id BIGINT NOT NULL,
  system_quantity INT NOT NULL,
  counted_quantity INT NOT NULL,
  difference_qty INT NOT NULL,
  counted_by VARCHAR(64) NOT NULL,
  counted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(16) NOT NULL DEFAULT 'draft',
  remark VARCHAR(255) DEFAULT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_counts_medicine FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS adjustment_orders (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  order_no VARCHAR(64) NOT NULL UNIQUE,
  count_id BIGINT DEFAULT NULL,
  medicine_id BIGINT NOT NULL,
  system_quantity INT NOT NULL,
  counted_quantity INT NOT NULL,
  difference_qty INT NOT NULL,
  reason VARCHAR(255) NOT NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'pending',
  created_by BIGINT NOT NULL,
  approved_by BIGINT DEFAULT NULL,
  approved_at DATETIME DEFAULT NULL,
  remark VARCHAR(255) DEFAULT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_adjust_count FOREIGN KEY (count_id) REFERENCES stock_counts(id) ON DELETE SET NULL,
  CONSTRAINT fk_adjust_medicine FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE RESTRICT,
  CONSTRAINT fk_adjust_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT,
  CONSTRAINT fk_adjust_approved_by FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS expiry_warnings (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  medicine_id BIGINT NOT NULL,
  batch_id BIGINT NOT NULL,
  warning_type VARCHAR(32) NOT NULL,
  days_left INT NOT NULL,
  warning_level VARCHAR(16) NOT NULL,
  generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(16) NOT NULL DEFAULT 'active',
  CONSTRAINT fk_warning_medicine FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE,
  CONSTRAINT fk_warning_batch FOREIGN KEY (batch_id) REFERENCES medicine_batches(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS purchase_orders (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  order_no VARCHAR(64) NOT NULL UNIQUE,
  medicine_id BIGINT NOT NULL,
  supplier_id BIGINT NOT NULL,
  requested_qty INT NOT NULL,
  suggested_qty INT NOT NULL,
  reason VARCHAR(255) NOT NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'pending',
  created_by BIGINT NOT NULL,
  reviewed_by BIGINT DEFAULT NULL,
  reviewed_at DATETIME DEFAULT NULL,
  remark VARCHAR(255) DEFAULT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_purchase_medicine FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE RESTRICT,
  CONSTRAINT fk_purchase_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE RESTRICT,
  CONSTRAINT fk_purchase_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT,
  CONSTRAINT fk_purchase_reviewed_by FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO users (id, username, password_hash, nickname, role, phone, email, status)
VALUES
  (1, 'admin', 'pbkdf2_sha256$390000$y3Qv6pYxg8m3G4nU$JBY4R4X1fLJ55Vx0qfX1pD7m3V7jQ9u7QY5bQ7f0c5s=', '系统管理员', 'admin', '13800000000', 'admin@clinic.local', 'enabled')
ON DUPLICATE KEY UPDATE username = VALUES(username);

INSERT INTO users (id, username, password_hash, nickname, role, phone, email, status)
VALUES
  (2, 'pharmacy', 'pbkdf2_sha256$390000$Qd8YfT8L7g0x9QpR$2sM9P4u3V4R2fFf8w8j4k0TQ1M0X7Q0S2pC6Qw0oF5I=', '药房管理员', 'pharmacist', '13800000001', 'pharmacy@clinic.local', 'enabled'),
  (3, 'doctor', 'pbkdf2_sha256$390000$5mF8P1yN0k4R7zVd$6xQ2S9mP3vT8uR1nL5wE4dF7gH2jK6lQ8pZ1cN4vB0=', '门诊医生', 'doctor', '13800000002', 'doctor@clinic.local', 'enabled'),
  (4, 'buyer', 'pbkdf2_sha256$390000$1pQ9xZ8sV7nD3fKj$8yH4mL2cW5rT6uV9bN1dF7gJ3kP0qR4sT8wX2zM6aC=', '采购员', 'purchaser', '13800000003', 'buyer@clinic.local', 'enabled')
ON DUPLICATE KEY UPDATE username = VALUES(username);

INSERT INTO suppliers (id, name, contact_person, phone, email, address, supply_scope, status)
VALUES
  (1, '华康医药配送中心', '陈经理', '021-55550001', 'service@huakang.com', '上海市浦东新区医药路88号', '处方药、常用耗材', 'active'),
  (2, '益民药业有限公司', '刘经理', '020-55550002', 'sales@yimin.com', '广州市天河区健康大道66号', '慢病药品、OTC常备药', 'active')
ON DUPLICATE KEY UPDATE name = VALUES(name);

INSERT INTO medicines
  (id, code, name, specification, unit, category, current_stock, safety_stock, selling_price, purchase_price, expiry_warning_days, supplier_id, location, status)
VALUES
  (1, 'MED-001', '阿莫西林胶囊', '0.25g*24粒', '盒', '抗感染药', 168, 50, 18.00, 12.30, 90, 1, 'A01-01', 'active'),
  (2, 'MED-002', '布洛芬缓释胶囊', '0.3g*20粒', '盒', '解热镇痛药', 92, 40, 22.00, 15.50, 120, 2, 'A01-02', 'active'),
  (3, 'MED-003', '葡萄糖注射液', '500ml', '瓶', '静脉输液', 36, 20, 8.50, 5.80, 60, 1, 'B02-03', 'active')
ON DUPLICATE KEY UPDATE code = VALUES(code);

INSERT INTO medicine_batches
  (id, medicine_id, supplier_id, batch_no, inbound_order_no, quantity, remaining_quantity, production_date, expiry_date, inbound_date, location, remark, status)
VALUES
  (1, 1, 1, 'A20250301', 'IN-20250401001', 200, 168, '2025-03-01', '2026-02-28', '2025-04-01 09:00:00', 'A01-01', '首批示例批次', 'available'),
  (2, 2, 2, 'B20250405', 'IN-20250405002', 120, 92, '2025-04-05', '2026-07-31', '2025-04-05 11:30:00', 'A01-02', '门诊常用批次', 'available'),
  (3, 3, 1, 'C20250320', 'IN-20250408003', 50, 36, '2025-03-20', '2025-11-20', '2025-04-08 16:20:00', 'B02-03', '液体药品批次', 'available')
ON DUPLICATE KEY UPDATE batch_no = VALUES(batch_no);

INSERT INTO inbound_orders
  (id, order_no, medicine_id, supplier_id, batch_id, batch_no, quantity, purchase_price, received_by, received_at, status, remark)
VALUES
  (1, 'IN-20250401001', 1, 1, 1, 'A20250301', 200, 12.30, '药房管理员', '2025-04-01 09:00:00', 'completed', '示例入库'),
  (2, 'IN-20250405002', 2, 2, 2, 'B20250405', 120, 15.50, '药房管理员', '2025-04-05 11:30:00', 'completed', '示例入库'),
  (3, 'IN-20250408003', 3, 1, 3, 'C20250320', 50, 5.80, '药房管理员', '2025-04-08 16:20:00', 'completed', '示例入库')
ON DUPLICATE KEY UPDATE order_no = VALUES(order_no);

INSERT INTO prescription_issues
  (id, issue_no, patient_name, doctor_name, issued_by, issued_at, total_amount, status, remark)
VALUES
  (1, 'PR-20250408001', '王女士', '张医生', 3, '2025-04-08 10:20:00', 54.00, 'completed', '发热处方示例'),
  (2, 'PR-20250409001', '李先生', '张医生', 3, '2025-04-09 14:35:00', 18.00, 'completed', '止痛处方示例')
ON DUPLICATE KEY UPDATE issue_no = VALUES(issue_no);

INSERT INTO prescription_issue_items
  (id, issue_id, medicine_id, batch_id, quantity, unit_price)
VALUES
  (1, 1, 2, 2, 2, 22.00),
  (2, 2, 1, 1, 1, 18.00)
ON DUPLICATE KEY UPDATE issue_id = VALUES(issue_id);

INSERT INTO stock_counts
  (id, count_no, medicine_id, system_quantity, counted_quantity, difference_qty, counted_by, counted_at, status, remark)
VALUES
  (1, 'SC-20250410001', 1, 168, 165, -3, '药房管理员', '2025-04-10 17:20:00', 'submitted', '盘点差异示例'),
  (2, 'SC-20250410002', 2, 92, 92, 0, '药房管理员', '2025-04-10 17:25:00', 'submitted', '盘点一致')
ON DUPLICATE KEY UPDATE count_no = VALUES(count_no);

INSERT INTO adjustment_orders
  (id, order_no, count_id, medicine_id, system_quantity, counted_quantity, difference_qty, reason, status, created_by, approved_by, approved_at, remark)
VALUES
  (1, 'ADJ-20250410001', 1, 1, 168, 165, -3, '盘点差异', 'pending', 2, NULL, NULL, '等待管理员确认')
ON DUPLICATE KEY UPDATE order_no = VALUES(order_no);

INSERT INTO expiry_warnings
  (id, medicine_id, batch_id, warning_type, days_left, warning_level, generated_at, status)
VALUES
  (1, 3, 3, '近效期预警', 195, 'info', '2025-05-01 09:00:00', 'active')
ON DUPLICATE KEY UPDATE medicine_id = VALUES(medicine_id);

INSERT INTO purchase_orders
  (id, order_no, medicine_id, supplier_id, requested_qty, suggested_qty, reason, status, created_by, reviewed_by, reviewed_at, remark)
VALUES
  (1, 'PO-20250415001', 1, 1, 120, 100, '阿莫西林安全库存不足，建议补货', 'pending', 4, NULL, NULL, '待采购审批'),
  (2, 'PO-20250415002', 3, 2, 60, 40, '葡萄糖注射液库存偏低，建议补货', 'pending', 4, NULL, NULL, '待采购审批')
ON DUPLICATE KEY UPDATE order_no = VALUES(order_no);

SET FOREIGN_KEY_CHECKS = 1;
