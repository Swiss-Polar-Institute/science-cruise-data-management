#!/bin/bash

docker run --name mysql-glace \
	-e MYSQL_ROOT_PASSWORD=glace \
	-e MYSQL_USER=glace \
	-e MYSQL_PASSWORD=glace \
	-e MYSQL_DATABASE=glace \
	-p 3306:3306 \
	-d mysql:8 \
	--character-set-server=utf8mb4 \
	--collation-server=utf8mb4_unicode_ci \
	--default-authentication-plugin=mysql_native_password


