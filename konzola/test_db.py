from databaza.db import get_connection

def main():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM klient")
    count = cursor.fetchone()[0]
    print("Pocet klientov v DB:", count)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
