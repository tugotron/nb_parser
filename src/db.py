from peewee import SqliteDatabase, Model, IntegerField, IntegrityError, DoesNotExist


DB = SqliteDatabase('chat_ids.db')


class Chat(Model):
    chat_id = IntegerField(unique=True)

    class Meta:
        database = DB


class Gateway:
    def __init__(self):
        self.db = DB
        self.db.connect()
        self.db.create_tables([Chat])

    def __del__(self):
        self.db.close()

    def save(self, chat_id):
        try:
            with self.db.atomic():
                Chat.create(chat_id=chat_id)
        except IntegrityError:
            pass

    def get_ids(self):
        return {c.chat_id for c in Chat.select()}

    def remove_id(self, chat_id):
        try:
            with self.db.atomic():
                instance = Chat.get(Chat.chat_id == chat_id)
                instance.delete_instance()
        except DoesNotExist:
            pass
