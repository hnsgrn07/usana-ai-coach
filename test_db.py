import psycopg2

conn = psycopg2.connect(
    "postgresql://neondb_owner:npg_UYbG6HV5jJRp@ep-silent-hat-ay4gfwwn-pooler.c-5.us-east-2.aws.neon.tech/neondb?sslmode=require"
)
print("Connected successfully!")
conn.close()