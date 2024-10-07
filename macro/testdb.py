from db import database

db = database()
# db.delete_all()
# db.add_activity("My Program", "My Window", 120)
# Filter programs by specific day
print(db.filter_by(3, 10, 2024))
print(db.filter_by(month=10, year=2024))
# print(db.filter_by(year=2024))
# print(db.filter_by(month=10))
