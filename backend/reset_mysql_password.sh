#!/bin/bash

# 停止MySQL服务
echo "停止MySQL服务..."
brew services stop mysql

# 等待服务停止
sleep 3

# 以跳过权限表的方式启动MySQL
echo "以跳过权限表方式启动MySQL..."
mysqld_safe --skip-grant-tables &

# 等待MySQL启动
sleep 5

# 重置root密码
echo "重置root密码..."
mysql -u root << EOF
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'Xiaochuan123!';
FLUSH PRIVILEGES;
EOF

# 停止MySQL
echo "停止MySQL..."
pkill -f mysqld

# 等待停止
sleep 3

# 正常启动MySQL服务
echo "正常启动MySQL服务..."
brew services start mysql

# 等待启动
sleep 5

# 测试连接
echo "测试数据库连接..."
mysql -u root -pXiaochuan123! -e "SHOW DATABASES;"

echo "MySQL密码重置完成！"