import json
import unittest
from dbmigrator.configuration_management.db_credentials import mysql_credentials
from dbmigrator.database_connections.mysql_connection import MySQLConnection
from dbmigrator.data_access.mysql_metadata_reader import fetch_table_info, fetch_columns_info, fetch_constraints_info, \
    fetch_indexes_info



class TestMetadata(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mysql_conn = MySQLConnection(mysql_credentials())
        cls.mysql_conn.create()

    @classmethod
    def tearDownClass(cls):
        cls.mysql_conn.close()

    def test_search_table(self):
        table = fetch_table_info(self.mysql_conn, 'device_transfers')
        self.assertIsNotNone(table, 'The table is None.')
        self.assertEqual(table.name, 'device_transfers', 'Table name does not match')

    def test_search_table_columns(self):
        columns = fetch_columns_info(self.mysql_conn, 'device_transfers')
        self.assertIsNotNone(columns, 'The Columns are None.')
        self.assertTrue(len(columns) > 0, 'No columns found in the table')

        expected_columns = ['id', 'device_id', 'origin_name', 'destiny_name', 'origin_dispatch_group_id',
                            'destiny_dispatch_group_id', 'origin_tracking_id', 'destiny_tracking_id', 'origin_imei',
                            'destiny_imei', 'origin_vehicle_id', 'destiny_vehicle_id', 'created_user_id',
                            'transfered_at', 'to_be_returned_at', 'automatic_return', 'returned_at', 'created_at',
                            'updated_at', 'deleted_at', 'canceled_user_id', 'modified_user_id']
        for column in expected_columns:
            self.assertTrue(any(col.name == column for col in columns), f'Column {column} not found')

    def test_fetch_constraints_info(self):
        constraints = fetch_constraints_info(self.mysql_conn, 'device_transfers')
        self.assertIsNotNone(constraints, 'The Constraints are None.')

        expected_constraints = ['device_transfers_canceled_user_id_foreign',
                                'device_transfers_destiny_dispatch_group_id_foreign',
                                'device_transfers_destiny_vehicle_id_foreign', 'device_transfers_device_id_foreign',
                                'device_transfers_modified_user_id_foreign',
                                'device_transfers_origin_dispatch_group_id_foreign',
                                'device_transfers_origin_vehicle_id_foreign', 'device_transfers_user_id_foreign']
        for constraint in expected_constraints:
            self.assertTrue(any(con.name == constraint for con in constraints), f'Constraint {constraint} not found')

    def test_fetch_indexes_info(self):
        indexes = fetch_indexes_info(self.mysql_conn, 'device_transfers')
        self.assertIsNotNone(indexes, 'The Indexes are None.')

        expected_indexes = ['PRIMARY', 'device_transfers_device_id_index',
                            'device_transfers_origin_dispatch_group_id_index',
                            'device_transfers_destiny_dispatch_group_id_index', 'device_transfers_user_id_index',
                            'device_transfers_canceled_user_id_index', 'device_transfers_modified_user_id_index',
                            'device_transfers_origin_vehicle_id_index', 'device_transfers_destiny_vehicle_id_index']
        for index in expected_indexes:
            self.assertTrue(any(ind.name == index for ind in indexes), f'Index {index} not found')


if __name__ == '__main__':
    unittest.main()
