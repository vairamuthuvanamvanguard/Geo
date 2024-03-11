import psycopg2

# Define your bounding box [minLon, minLat, maxLon, maxLat]
bbox = [-74.0060, 40.7128, -73.9352, 40.7308]  # Example coordinates for a part of New York

# Database connection details
conn = psycopg2.connect("dbname='geoapp' user='postgres' host='localhost' password='muthu12345' port='5432'")

# SQL query to select items within the bounding box
sql_query = """
SELECT id, name, ST_AsText(geom) 
FROM public 
WHERE ST_Within(geom, ST_MakeEnvelope(%s, %s, %s, %s, 4326));
"""

# Execute the query
with conn.cursor() as cur:
    cur.execute(sql_query, bbox)
    rows = cur.fetchall()

# Close the database connection
conn.close()

# Example output
for row in rows:
    print(row)
