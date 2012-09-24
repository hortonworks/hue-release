from command import Command

class HCatClient(Command):

    def get_tables(self, dbname, tbl_name):
        #result = ["table12", "table33"]
        result = []
        command = Command()
        ret = command.execute('SHOW TABLES')
        if ret != False:
            result = ret.splitlines()
        #answer = command.last_error
        #answer = ret
        return result
