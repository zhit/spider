-- 爬虫SQL


-- 删除表
DROP TABLE product;
DROP TABLE store;
DROP TABLE category_2nd;
DROP TABLE category_top;
DROP TABLE category_industry;
-- 删除序列
DROP SEQUENCE product_id_seq;
DROP SEQUENCE store_id_seq;
DROP SEQUENCE category_2nd_id_seq;
DROP SEQUENCE category_top_id_seq;
DROP SEQUENCE category_industry_id_seq;
-- 删除索引
DROP INDEX product_href;
DROP INDEX product_category_id;
DROP INDEX store_homepage;
DROP INDEX store_linkman;

-- 行业分类表
CREATE TABLE category_industry
(
  category_industry_id integer NOT NULL,
  category_name character varying(255),
  CONSTRAINT category_industry_pkey PRIMARY KEY (category_industry_id)
);
-- 序列 start 10000
CREATE SEQUENCE category_industry_id_seq
    START WITH 10000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;  
alter table category_industry alter column category_industry_id set default nextval('category_industry_id_seq');

-- 一级分类表
CREATE TABLE category_top
(
  category_top_id integer NOT NULL,
  category_name character varying(255),
  category_industry_id integer,
  CONSTRAINT category_top_pkey PRIMARY KEY (category_top_id),
  CONSTRAINT category_top_category_industry_id_fkey FOREIGN KEY (category_industry_id)
      REFERENCES category_industry (category_industry_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
);
-- 序列 start 10000
CREATE SEQUENCE category_top_id_seq
    START WITH 10000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;  
alter table category_top alter column category_top_id set default nextval('category_top_id_seq');

-- 二级分类表
CREATE TABLE category_2nd
(
  category_2nd_id integer NOT NULL,
  category_name character varying(255),
  category_href character varying(255),
  category_top_id integer,
  CONSTRAINT category_2nd_pkey PRIMARY KEY (category_2nd_id),
  CONSTRAINT category_2nd_category_top_id_fkey FOREIGN KEY (category_top_id)
      REFERENCES category_top (category_top_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
);
-- 序列 start 10000
CREATE SEQUENCE category_2nd_id_seq
    START WITH 10000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;  
alter table category_2nd alter column category_2nd_id set default nextval('category_2nd_id_seq');

-- 公司联系信息表
CREATE TABLE store
(
  store_id integer NOT NULL,
  store_name character varying(255),
  store_homepage character varying(255),
  linkman character varying(255),
  telephone character varying(255),
  mobile_phone character varying(255),
  other_phone character varying(255),
  fax character varying(255),
  address text,
  CONSTRAINT store_pkey PRIMARY KEY (store_id)
);
-- 序列 start 10000
CREATE SEQUENCE store_id_seq
    START WITH 10000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;  
alter table store alter column store_id set default nextval('store_id_seq');
-- 创建索引
CREATE INDEX store_homepage ON store(store_homepage);
CREATE INDEX store_linkman ON store(linkman);


-- 产品表
CREATE TABLE product
(
  product_id integer NOT NULL,
  product_name character varying(255),
  price numeric(18,3),
  quantity_uom_id character varying(20),
  currency_uom_id character varying(20),
  product_href character varying(255),
  product_img_0 character varying(255),
  product_img_1 character varying(255),
  product_img_2 character varying(255),
  product_img_3 character varying(255),
  product_img_4 character varying(255),
  product_img_5 character varying(255),
  product_img_6 character varying(255),
  product_img_7 character varying(255),
  description text,
  long_description text,
  category_2nd_id integer,
  store_id integer,
  CONSTRAINT product_pkey PRIMARY KEY (product_id),
  CONSTRAINT product_category_2nd_id_fkey FOREIGN KEY (category_2nd_id)
      REFERENCES category_2nd (category_2nd_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT product_store_id_fkey FOREIGN KEY (store_id)
      REFERENCES store (store_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
);
-- 序列 start 10000
CREATE SEQUENCE product_id_seq
    START WITH 10000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;  
alter table product alter column product_id set default nextval('product_id_seq');
-- 创建索引
CREATE INDEX product_href ON product(product_href);
CREATE INDEX product_category_id ON product(category_2nd_id);

-- 改变序列start

-- alter sequence category_industry_id_seq restart with 10000;
-- alter sequence category_top_id_seq restart with 10000;
-- alter sequence category_2nd_id_seq restart with 10000;
-- alter sequence product_id_seq restart with 10000;
-- alter sequence store_id_seq restart with 10000;

-- 数据表 store 导出成store.csv文件格式
-- COPY store TO 'D:\\store.csv' CSV HEADER;
-- 在Linu环境下可能会出现无读写权限问题：请将需要拷贝的路径所涉及到得文件夹权限修改为其他人可执行（其他用户可访问），且store.csv文件为其他人可读可写。
-- 		例如：COPY store TO '/home/feihua/store.csv' CSV HEADER; 需要将home feihua文件夹都设置为rwxr-xr-x store.csv设置为rw-r--rw-
-- 		参考：https://www.postgresql.org/message-id/AANLkTikNM3uJAAaVTXnt-%2BboKALWsURCQkgvicN7GEaZ%40mail.gmail.com

-- 数据表插入多行数据：
-- 添加多条记录：INSERT INTO tableName(col1,col2,col3) SELECT 3,4,5  UNION ALL  SELECT 6,7,8 
-- 从另外的一张表中读取多条数据添加到新表中：INSERT INTO tableName(col1,col2,col3) SELECT a,b,c FROM tableA 
-- 从其他的多张表中读取数据添加到新表中：INSERT INTO tableName(col1,col2,col3) SELECT a,b,c FROM tableA WHERE a=1 UNION ALL SELECT a,b,c FROM tableB WHERE a=2  
-- 当需要插入固定值到新列时：INSERT INTO tableName(col1,col2,col3,col4) SELECT 'china',a,b,c FROM tableA 在新表col1插入固定值'china'
-- 当需要插入当前时间到新列时：INSERT INTO tableName(col1,col2,col3,col4) SELECT Now(),a,b,c FROM tableA 在新表col1插入当前时间
  
-- postgres 执行SQL文件
-- psql \i C:/爬虫SQL.sql

-- postgres 备份与恢复（pg_dump命令会备份表结构、序列、索引及数据等，在恢复时无需创建表，只创建数据库即可）
-- 1.备份整个数据库到指定目录（表结构和数据）
-- 进入到\PostgreSQL\9.4\bin>目录下执行pg_dump.exe  -U postgres -d dbname > "D:\dbname.sql"
-- 2.备份单个数据表到指定目录（表结构和数据）
-- 进入到\PostgreSQL\9.4\bin>目录下执行pg_dump.exe  -U postgres -t tablename dbname > "D:\tablename.sql"
-- 3.恢复所有表到指定数据库（表结构和数据）
-- 执行psql -h 127.0.0.1 -U feihua -d dbname -p 5432 -f /home/feihua/soft/dbname.sql
-- 4.恢复单个表到指定数据库（表结构和数据）
-- 执行psql -h 127.0.0.1 -U feihua -d dbname -p 5432 -f /home/feihua/soft/tablename.sql

-- 通常使用如下方式：
-- 导出：pg_dump -h 127.0.0.1 -p 5432 -U postgres -d dbname -t table -F t -v -f D:\\dbname.tar  （或pg_dump -h 127.0.0.1 -p 5432 -U postgres -F t -v -f D:\\dbname.tar dbname）
-- 导入：pg_restore -h 127.0.0.1 -p 5432 -U postgres -d dbname -v -i D:\\dbname.tar 

-- 针对大数据备份：
-- 方法1：使用unix管道来直接压缩（压缩率优于方法2，但仅可在Linux环境下备份和恢复）
-- 导出：pg_dump -h 127.0.0.1 -p 5432 -U postgres -d dbname -t table | gzip > /home/dbname_backup.gz 
-- 导入：gunzip -c /home/dbname_backup.gz | psql -h 127.0.0.1 -p 5432 -U postgres -d dbname -t table -v
-- 方法2：使用custom-dump（通常采用此方法）
-- 导出：pg_dump -h 127.0.0.1 -p 5432 -U postgres -d dbname -t table -F c -f /home/dbname_backup.dump
-- 导入：pg_restore -h 127.0.0.1 -p 5432 -U postgres -d dbname -v -i /home/dbname_backup.dump

-- 出现问题及解决办法：
-- 1.windows下可能会出现fe_sendauth: no password supplied错误，需要将pg_hba.conf文件下IPv4 127.0.0.1/32 认证方式修改为 trust，并重启postgreSQL服务
-- 2.CentOS下pg_dump命令可能会与服务器版本不匹配的问题，需要使用高版本替换低版本解决。具体操作：
---  （1）.使用find / -name pg_dump -type f 2>/dev/null 查找所有pg_dump命令。
---  （2）.若存在多个，则使用创建链接形式指向高版本，sudo ln -s /usr/pgsql-9.4/bin/pg_dump /usr/bin/pg_dump --force 
-- 参考：http://blog.csdn.net/rgb_rgb/article/details/16954435  http://www.postgres.cn/docs/9.4/app-pgdump.html