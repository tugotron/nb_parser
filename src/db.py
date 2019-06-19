from peewee import SqliteDatabase, Model, IntegerField, IntegrityError, DoesNotExist


db = SqliteDatabase('chat_ids.db')


class Chat(Model):
    chat_id = IntegerField(unique=True)

    class Meta:
        database = db


class Gateway:
    def __init__(self):
        self.db = SqliteDatabase('chat_ids.db')
        self.db.connect()

    def __del__(self):
        self.db.close()

    def create_tables(self):
        db.create_tables([Chat])

    def save(self, chat_id):
        try:
            with db.atomic():
                Chat.create(chat_id=chat_id)
        except IntegrityError:
            pass

    def get_ids(self):
        return {c.chat_id for c in Chat.select()}

    def remove_id(self, chat_id):
        try:
            with db.atomic():
                instance = Chat.get(Chat.chat_id == chat_id)
                instance.delete_instance()
        except DoesNotExist:
            pass
