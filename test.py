import pymysql.cursors
import logging


logging.basicConfig(level=logging.DEBUG)

try:
    connection = pymysql.connect(
        host='bhyb1fa898t0ow9ufdlc-mysql.services.clever-cloud.com',
        user='uezytq7dxx48hp8w',
        password='s18HO1qr2Nw46fXbuHPg',
        database='bhyb1fa898t0ow9ufdlc',
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=60  # Increased timeout
    )

    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            result = cursor.fetchone()
            print(result)
except pymysql.MySQLError as e:
    print("Error:", e)
