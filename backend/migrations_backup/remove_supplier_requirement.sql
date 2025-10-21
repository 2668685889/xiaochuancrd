-- 修改products表，将supplier_uuid字段改为允许为null
USE xiaochuanERP;
ALTER TABLE products MODIFY supplier_uuid CHAR(36) NULL;