import sqlalchemy.orm
from sqlalchemy import Table, Index, Integer, String, Column, Text, Float, \
                       DateTime, Boolean, PrimaryKeyConstraint, \
                       UniqueConstraint, ForeignKeyConstraint, orm
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session

from datetime import datetime
rooms_db = 'db/rooms-sqlite3.db'


Base = declarative_base()

class Rooms(Base):
    __tablename__='rooms'
    # id = Column(Integer(), primary_key=True)
    # room_id = Column(String(20), nullable=False)
    room_id = Column(String(20), primary_key=True)
    floor = Column(Integer, default=None)
    for_rent = Column(Boolean(), default=False)
    price = Column(Integer(), default=None)
    occupied = Column(Boolean(), default=False)
    rented_from = Column(DateTime(), default=None)
    rented_to = Column(DateTime(), default=None)
    need_attention = Column(Boolean(), default=False)
    need_cleaning = Column(Boolean(), default=False)
    need_repair = Column(Boolean(), default=False)
    need_electric_repair = Column(Boolean(), default=False)
    need_water_repair = Column(Boolean(), default=False)
    comment = Column(Text(), default='')
    comment_tech = Column(Text(), default='')


class Signs:
    need_attention = '‼️' # '🛑'  🔴🔵💦🐳⚡💧😜😐
    for_rent = '✅'
    not_for_rent = '🔴'
    occupied = '😎'
    room_free = '🆓'
    need_cleaning = '🚿'
    all_is_good = '🆗'  # 👍
    need_repair = '🔵'
    need_electric_repair = '⚡'  # '⚠️'
    need_water_repair = '🐳'
    yes = '🔴'

sign = Signs


class Room_DB():
    def __init__(self):
        self.engine = create_engine(f'sqlite:///{rooms_db}')
        self.engine.connect()
        self.session = Session(bind=self.engine)

    def create_rooms_table(self):
        Base.metadata.create_all(self.engine)

    def room_create(self, room: str, room_price=None, room_for_rent=False, room_comment='', room_floor=None):
        # global session
        room_id = Rooms(
            room_id=str(room),
            price=room_price,
            for_rent=room_for_rent,
            comment=room_comment,
            floor=room_floor
        )
        self.session.add_all([room_id])
        self.session.commit()

    def remove_all_tables(self):
        input('Are you sure to remove all tables? Ctrl+C in not.')
        Base.metadata.drop_all(bind=self.engine)
        self.session.commit()

    def get_all_rooms_list(self):
        query_result = self.session.query(Rooms).all()
        for room in query_result:
            # print(f'Floor:{room.floor}\t{room.room_id}, {room.price}$,\t{room.occupied},\t{room.comment}')
            room_description = f'{room.room_id}'
            if room.for_rent:
                room_description += f' {sign.for_rent} сдается'
            else:
                room_description += f' {sign.not_for_rent} не сдается'
            if room.price:
                room_description += f' за {room.price}$'
            if room.occupied:
                room_description += f' заселен {sign.occupied}'
            yield room.room_id, room_description

    def get_rooms_list(self):
        rooms = self.session.query(Rooms).filter(Rooms.for_rent==True).all()
        for room in rooms:
            # print(f'{room.room_id}, {room.price}$, {room.occupied}, {room.comment}')
            room_description = f'{room.room_id}'
            # if room.for_rent:
            #     return_string += f'{sign.for_rent}'
            if room.price:
                room_description += f' {room.price}$'
            if room.occupied:
                room_description += f' {sign.occupied}'
                if room.rented_to:
                    room_description += f' {room.rented_to}'
            else:
                room_description += f' {sign.room_free}'
            if room.need_cleaning:
                room_description += f' {sign.need_cleaning}'
            if not room.need_cleaning and not room.need_attention and not room.need_electric_repair and not room.need_water_repair:
                room_description += f' {sign.all_is_good}'
            if room.need_attention:
                room_description += f' {sign.need_attention}'
            if room.need_repair:
                room_description += f' {sign.need_repair}'
            if room.need_electric_repair:
                room_description += f' {sign.need_electric_repair}'
            if room.need_water_repair:
                room_description += f' {sign.need_water_repair}'
            if room.comment:
                room_description += f' {room.comment} '
            if room.comment_tech:
                room_description += f' {room.comment_tech} '
            yield room.room_id, room_description


    def get_free_rooms_list(self):
        rooms = self.session.query(Rooms).filter(Rooms.for_rent==True, Rooms.occupied==False).all()
        for room in rooms:
            # print(f'Free room: {room.room_id}, {room.price}$, {room.rented_from}, {room.comment}')
            room_description = f'{room.room_id}'
            if room.price:
                room_description += f' {room.price}$'
            if room.occupied:
                room_description += f' {sign.occupied}'
            else:
                room_description += f' {sign.room_free}'
            if room.need_cleaning:
                room_description += f' {sign.need_cleaning}нужна уборка'
            if not room.need_cleaning and not room.need_attention and\
                    not room.need_repair and not room.need_electric_repair and not room.need_water_repair:
                room_description += f' {sign.all_is_good}'
            if room.need_attention:
                room_description += f' {sign.need_attention}'
            if room.need_repair:
                room_description += f' {sign.need_repair}'
            if room.need_electric_repair:
                room_description += f' {sign.need_electric_repair}'
            if room.need_water_repair:
                room_description += f' {sign.need_water_repair}'
            if room.comment:
                room_description += f' {room.comment} '
            if room.comment_tech:
                room_description += f' {room.comment_tech} '
            yield room.room_id, room_description


    def get_rooms_need_cleaning_list(self):
        rooms = self.session.query(Rooms).filter(Rooms.need_cleaning==True).all()
        for room in rooms:
            room_description = f'Номер {room.room_id}'
            if room.occupied:
                room_description += f' {sign.occupied}'
            else:
                room_description += f' {sign.room_free}'
            if room.comment:
                room_description += f' {room.comment} '
            if room.comment_tech:
                room_description += f' {room.comment_tech} '
            yield room.room_id, room_description


    def get_rooms_need_technician(self):
        rooms = self.session.query(Rooms).filter((Rooms.need_attention==True)|
                                                 (Rooms.need_repair==True)|
                                                 (Rooms.need_electric_repair==True)|
                                                 (Rooms.need_water_repair==True)|
                                                 (Rooms.comment_tech==True)
                                                 ).all()
        for room in rooms:
            room_description = f'Номер {room.room_id}'
            if room.need_attention:
                room_description += f' {sign.need_attention}'
            if room.need_repair:
                room_description += f' {sign.need_repair}'
            if room.need_electric_repair:
                room_description += f' {sign.need_electric_repair}'
            if room.need_water_repair:
                room_description += f' {sign.need_water_repair}'
            if room.comment:
                room_description += f' {room.comment} '
            if room.comment_tech:
                room_description += f' {room.comment_tech} '
            yield room.room_id, room_description


    def get_room_property(self, room_id):
        # q = session.query(Rooms).get(room_id)
        q = self.session.get(Rooms, room_id)
        # print(f'{q.room_id}, {q.price}$, Occuped: {q.occupied}')
        return {'room_id': q.room_id,
                'occupied': q.occupied,
                'need_cleaning': q.need_cleaning,
                'need_attention': q.need_attention,
                'need_repair': q.need_repair, 'need_water_repair': q.need_water_repair,
                'need_electric_repair': q.need_electric_repair}

    def room_init_anorita(self):
        # 205 , 204 , 304 , 305 - 400$
        # Остальные за 300$
        rooms_400 = (205, 204, 304, 305, 404, 405)
        self.remove_all_tables()
        self.create_rooms_table()
        self.room_create('101', room_for_rent=False, room_floor=1)
        for room_name in list(range(201, 212)) + list(range(301, 312)) + list(range(401, 412)):
            room_floor = int(int(room_name/100))
            if int(room_name) >= 400:
                self.room_create(room_name, room_for_rent=False, room_floor=room_floor)
                continue
            if int(room_name) in rooms_400:
                self.room_create(room_name, room_price=400, room_floor=room_floor)
            else:
                self.room_create(room_name, room_price=300, room_floor=room_floor)
            # print(room_name)
        for room_name in list(range(201, 212)) + list(range(301, 312)):
            self.set_room_for_rent(room_name)
            if room_name in (202 , 303 ):
                continue
            self.set_room_occuped(room_name)


    def change_room_occuped(self, room_id):
        room = self.session.get(Rooms, room_id)
        room.occupied = not room.occupied
        self.session.add(room)
        self.session.commit()
        room = self.session.get(Rooms, room_id)
        return room.occupied


    def change_room_need_cleaning(self, room_id):
        room = self.session.get(Rooms, room_id)
        room.need_cleaning = not room.need_cleaning
        self.session.add(room)
        self.session.commit()
        room = self.session.get(Rooms, room_id)
        return room.need_cleaning


    def change_room_need_electrician(self, room_id):
        room = self.session.get(Rooms, room_id)
        room.need_electric_repair = not room.need_electric_repair
        self.session.add(room)
        self.session.commit()
        room = self.session.get(Rooms, room_id)
        return room.need_electric_repair


    def change_room_need_waterrepair(self, room_id):
        room = self.session.get(Rooms, room_id)
        room.need_water_repair = not room.need_water_repair
        self.session.add(room)
        self.session.commit()
        room = self.session.get(Rooms, room_id)
        return room.need_water_repair

    def change_room_need_attention(self, room_id):
        room = self.session.get(Rooms, room_id)
        room.need_attention = not room.need_attention
        self.session.add(room)
        self.session.commit()
        room = self.session.get(Rooms, room_id)
        return room.need_attention

    def change_room_for_rent(self, room_id):
        room = self.session.get(Rooms, room_id)
        room.for_rent = not room.for_rent
        self.session.add(room)
        self.session.commit()
        room = self.session.get(Rooms, room_id)
        return room.for_rent


    def get_room_for_rent(self, room_id):
        room = self.session.get(Rooms, room_id)
        return room.for_rent


    def set_room_for_rent(self, room_id):
        room = self.session.get(Rooms, room_id)
        room.for_rent = True
        self.session.add(room)
        self.session.commit()
        return True


    def set_room_not_for_rent(self, room_id):
        room = self.session.get(Rooms, room_id)
        room.for_rent = False
        self.session.add(room)
        self.session.commit()
        return True


    def get_room_cost(self, room_id):
        room = self.session.get(Rooms, room_id)
        return room.price


    def set_room_cost(self, room_id, price: int):
        room = self.session.get(Rooms, room_id)
        try:
            room.price = int(price)
            self.session.add(room)
            self.session.commit()
            return True
        except Exception as e:
            print(e)
            return False


    def get_room_comment(self, room_id):
        room = self.session.get(Rooms, room_id)
        return room.comment


    def set_room_comment(self, room_id, comment: str):
        room = self.session.get(Rooms, room_id)
        room.comment = comment
        self.session.add(room)
        self.session.commit()


    def get_room_comment_tech(self, room_id):
        room = self.session.get(Rooms, room_id)
        return room.comment_tech


    def set_room_comment_tech(self, room_id, comment: str):
        room = self.session.get(Rooms, room_id)
        room.comment_tech = comment
        self.session.add(room)
        self.session.commit()


    def rooms_occuped_count(self):
        occuped_rooms = self.session.query(Rooms).filter(Rooms.occupied == True).all()
        return len(occuped_rooms)


    def rooms_need_cleaning_count(self):
        need_cleaning_rooms = self.session.query(Rooms).filter(Rooms.need_cleaning == True).all()
        return len(need_cleaning_rooms)


    def rooms_need_technician_count(self):
        need_technician_rooms = self.session.query(Rooms).filter(
            (Rooms.need_attention == True) |
            (Rooms.need_electric_repair == True) |
            (Rooms.need_water_repair == True)
        ).all()
        return len(need_technician_rooms)


    def rooms_free_count(self):
        free_rooms = self.session.query(Rooms).filter((Rooms.occupied == False),
                                                      (Rooms.for_rent == True)
                                                      ).all()
        return len(free_rooms)


if __name__ == '__main__':
    room_db = Room_DB()
    # room_db.room_init_anorita()
    # room_db.get_rooms_list()
    # exit(0)
    # get_room_property(201)
    # room_db.get_free_rooms_list()
    print()
    for room in room_db.get_rooms_list():
        print(room)
    pass
    # room_list = ( 202 , 303 , 311 )
    # for room_name in list(range(201, 212)) + list(range(301, 312)) + list(range(401, 412)):
    # for room_name in room_list:
    #     print(room_name)
    #     set_room_free(room_name)
    # set_room_comment(211, "Общая кухня")
    room_db.rooms_occuped_count()


