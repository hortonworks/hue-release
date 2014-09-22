INSERT INTO `x_user`
	(create_time, update_time, added_by_id, upd_by_id, user_name, descr, status, cred_store_id)
VALUES
	('2014-09-04 17:40:06','2014-09-04 17:40:06',1,1,'policymgr','policymgr',0,NULL);




INSERT INTO `x_asset`
	(create_time, update_time, added_by_id, upd_by_id, asset_name, descr, act_status, asset_type, config, sup_native)
VALUES
	('2014-09-04 17:40:06','2014-09-04 17:40:06',1,1,'Sandbox_HDFS','',1,1,
	'{\"username\":\"policymgr\",\"password\":\"policymgr\",\"fs.default.name\":\"hdfs://sandbox.hortonworks.com:8020\",\"hadoop.security.authorization\":\"true\",\"hadoop.security.authentication\":\"simple\",\"hadoop.security.auth_to_local\":\"\",\"dfs.datanode.kerberos.principal\":\"\",\"dfs.namenode.kerberos.principal\":\"\",\"dfs.secondary.namenode.kerberos.principal\":\"\",\"commonNameForCertificate\":\"\"}',
	0);

INSERT INTO `x_resource`
	(create_time, update_time, added_by_id, upd_by_id, res_name, descr, res_type, asset_id, parent_id, parent_path, is_encrypt, is_recursive, res_group, res_dbs, res_tables, res_col_fams, res_cols, res_udfs, res_status, table_type, col_type)
VALUES
	('2014-09-04 17:40:06','2014-09-04 17:40:06',1,1,'/',NULL,1,1,NULL,NULL,2,1,NULL,NULL,NULL,NULL,NULL,NULL,1,0,0);


INSERT INTO `x_audit_map`
	(create_time, update_time, added_by_id, upd_by_id, res_id, group_id, user_id, audit_type)
VALUES
	('2014-09-04 17:40:06','2014-09-04 17:40:06',1,1,1,NULL,NULL,1);

INSERT INTO `x_perm_map`
	(create_time, update_time, added_by_id, upd_by_id, perm_group, res_id, group_id, user_id, perm_for, perm_type, is_recursive, is_wild_card, grant_revoke)
VALUES
	('2014-09-04 17:40:06','2014-09-04 17:40:06',1,1,NULL,1,NULL,1,0,0,0,1,1);





INSERT INTO `x_asset`
	(create_time, update_time, added_by_id, upd_by_id, asset_name, descr, act_status, asset_type, config, sup_native)
VALUES
	('2014-09-04 17:54:06','2014-09-04 17:54:06',1,1,'Sandbox_Hive','',1,3,
	'{\"username\":\"policymgr\",\"password\":\"policymgr\",\"jdbc.driverClassName\":\"org.apache.hive.jdbc.HiveDriver\",\"jdbc.url\":\"jdbc:hive2://localhost:10000/default\",\"commonNameForCertificate\":\"\"}',
	0);

INSERT INTO `x_resource`
	(create_time, update_time, added_by_id, upd_by_id, res_name, descr, res_type, asset_id, parent_id, parent_path, is_encrypt, is_recursive, res_group, res_dbs, res_tables, res_col_fams, res_cols, res_udfs, res_status, table_type, col_type)
VALUES
	('2014-09-04 17:54:06','2014-09-04 17:54:06',1,1,'/*/*/*',NULL,1,2,NULL,NULL,2,0,NULL,'*','*',NULL,'*',NULL,1,0,0);

INSERT INTO `x_audit_map`
	(create_time, update_time, added_by_id, upd_by_id, res_id, group_id, user_id, audit_type)
VALUES
	('2014-09-04 17:54:06','2014-09-04 17:54:06',1,1,2,NULL,NULL,1);

INSERT INTO `x_perm_map`
	(create_time, update_time, added_by_id, upd_by_id, perm_group, res_id, group_id, user_id, perm_for, perm_type, is_recursive, is_wild_card, grant_revoke)
VALUES
	('2014-09-04 17:54:06','2014-09-04 17:54:06',1,1,NULL,2,NULL,1,0,0,0,1,1);
