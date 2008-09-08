from django.db.backends import BaseDatabaseIntrospection
from sqlalchemy import Table, types

class DatabaseIntrospection(BaseDatabaseIntrospection):
    data_types_reverse = {
        types.String: 'CharField',
        types.Text: 'TextField',
        types.Integer: 'IntegerField',
        types.Date: 'DateField',
        types.DateTime: 'DateTimeField',
        types.Float: 'FloatField',
        types.Time: 'TimeField',
        types.Integer: 'IntegerField',
        types.Numeric: 'DecimalField',
        types.SmallInteger: 'SmallIntegerField',
        types.Boolean: 'BooleanField',
    }

    def get_table_list(self, cursor):
        """
        Returns a list of tables in the current database.
        """    
        # Load all available table definitions from the database
        self.connection.metadata.reflect()
        
        return self.connection.metadata.tables.keys()

    def get_table_description(self, cursor, table_name):
        """
        Returns a description of the table, with the DB-API cursor.description interface.
        """
        t = Table(table_name, self.connection.metadata, autoload=True)
        result = t.select().limit(1).execute()

        return result.cursor.description

    def _name_to_index(self, cursor, table_name):
        """
        Returns a dictionary of {field_name: field_index} for the given table.
        Indexes are 0-based.
        """
        return dict([(d[0], i) for i, d in enumerate(self.get_table_description(cursor, table_name))])
    
    def get_relations(self, cursor, table_name):
        """
        Returns a dictionary of {field_index: (field_index_other_table, other_table)}
        representing all relationships to the given table. Indexes are 0-based.
        """
        my_field_dict = self._name_to_index(cursor, table_name)
        constraints = []
        relations = {}
        
        table = Table(table_name, self.connection.metadata, autoload=True)
        
        for fkey in table.foreign_keys:
            my_fieldname = fkey.parent.name
            other_table = fkey.column.table.name
            other_field = fkey.column.name
            constraints.append((my_fieldname, other_table, other_field))

        for my_fieldname, other_table, other_field in constraints:
            other_field_index = self._name_to_index(cursor, other_table)[other_field]
            my_field_index = my_field_dict[my_fieldname]
            relations[my_field_index] = (other_field_index, other_table)

        return relations
    
    def get_indexes(self, cursor, table_name):
        """
        Returns a dictionary of fieldname -> infodict for the given table,
        where each infodict is in the format:
        {'primary_key': boolean representing whether it's the primary key,
        'unique': boolean representing whether it's a unique index}
        """
        table = Table(table_name, self.connection.metadata, autoload=True)
        indexes = {}

        for column in table.columns:
            # note: sqlalchemy doesn't yet populate column.unique
            # and column.index upon reflection
            if column.primary_key:
                indexes[column.name] = {'primary_key': True,
                                        'unique': True,}
            elif column.unique:
                indexes[column.name] = {'primary_key': False,
                                        'unique': True,}
            elif column.index:
                indexes[column.name] = {'primary_key': False,
                                        'unique': False,}
        return indexes
