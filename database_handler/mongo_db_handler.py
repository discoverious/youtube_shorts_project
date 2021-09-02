import pymongo
from database_handler import mongo_db_settings
import os


class MongoDbHandler:
    def __init__(self, initial_db_name):
        self.client = pymongo.MongoClient(mongo_db_settings.MONGODB_CLIENT_URL)
        self.current_db = self.client[initial_db_name]

    def set_current_db(self, db_name):
        self.current_db = self.client[db_name]

    def delete_list_of_records(self, column_name, query):
        column_data = self.current_db[column_name]
        column_data.delete_many(query)

    def update_record(self, column_name, query_for_find, query_for_update):
        column_data = self.current_db[column_name]
        column_data.update_one(query_for_find, query_for_update)

    def insert_list_of_records(self, column_name, list_of_records):
        column_data = self.current_db[column_name]
        column_data.insert_many(list_of_records)

    def insert_record(self, column_name, record):
        column_data = self.current_db[column_name]
        column_data.insert_one(record)

    def search_list_of_records(self, column_name, query):
        column_data = self.current_db[column_name]
        list_of_doc_data = list(column_data.find(query))

        return list_of_doc_data

    def search_record(self, column_name, query):
        column_data = self.current_db[column_name]
        #column_data.limit(1).sort({$natural:-1})
        doc_data = column_data.find_one(query)

        return doc_data

    def search_recent_record(self, column_name):
        column_data = self.current_db[column_name]
        doc_data = column_data.find({}).limit(1).sort([("$natural",-1)])[0]

        return doc_data

    def search_recent_record_with_record(self, column_name, query):
        column_data = self.current_db[column_name]
        doc_data = column_data.find(query).limit(1).sort([("$natural",-1)]) #find(query).#

        if doc_data.count() != 0:
            return doc_data[0]

        else:
            return None
