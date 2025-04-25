# generic-data-ingestion

An easy, generic, and flexible data ingestion process built in Python, designed for extracting, cleaning, and loading data from diverse sources (Databases, CSV files, API). Ideal for ELT use cases and data engineering workflows.

---

## 🚀 How It Works

This script is designed to extract data from key sources (databases, CSV files, or APIs), apply basic adjustments and light preprocessing, and write the output in a standardized format (Iceberg Parquet).

![generic_ingestion](https://github.com/user-attachments/assets/c1798d04-aedf-4556-9bbc-2436a65d453f)


The script is fully parameterized through a JSON configuration, which ensures flexibility and reusability.

The JSON configuration must include three main keys:

1. **`source`** – Defines the origin of the data.
2. **`data`** – Specifies basic data transformations before writing.
3. **`destination`** – Defines where and how the processed data should be stored.

The script reads the JSON configuration and dynamically builds the ETL logic, making it easy to plug into multiple ingestion workflows.

---

## 🛠️ How to Use

1. 📥 Clone the repository

```bash
git clone https://github.com/rafael-aguiar-ramalho/generic-data-ingestion.git
cd generic-data-ingestion
```


2. 📦 Install dependencies

You can install the required packages using pip:

```bash
pip install -r requirements.txt
```

Make sure you also have **Java**, **Apache Spark** and **desired Spark Jars** installed and properly configured in your environment.


3. ⚙️ Prepare your JSON parameters file

The script expects a JSON file containing all the parameters.

1. **`source`** – Defines the origin of the data:
   - When `type` is **`csv`**:
     - `path`: path to the CSV file
     - `header`: whether the file has a header (`true` or `false`)
     - `separator`: field separator (e.g., `,`, `;`)
     - `encoding`: character encoding (e.g., `utf-8`)

   - When `type` is **`api`**:
     - `url`: API endpoint
     - `data_location_key`: key to locate the relevant data inside the response JSON
     - `optional_params`: dictionary of parameters (e.g., filters, pagination) if needed

   - When `type` is **`database`**:
     - `jdbc_driver`: driver class name (e.g., `org.postgresql.Driver`)
     - `url`: JDBC URL for the database
     - `query`: SQL query to extract the data
     - `user`: database user
     - `password`: database password
     - `execute_before_query`: SQL command to run before the main query (e.g., temp table setup)


2. **`data`** – Specifies basic data transformations before writing:
   - `rename`: a dictionary mapping old column names to new ones
   - `auto_trim`: boolean flag to automatically trim whitespace from all string columns (`true` or `false`)
   - `treat_columns`: list of column names that require somes specific basic transformation or cleaning
   - `schema`: dictionary specifying the complete data schema (column name, column type and column comment)
   - `py_columns`: dictionary of custom columns based on Python expressions


3. **`destination`** – Defines where and how the processed data should be stored:
   - `catalog`: name of the Spark catalog (e.g., `spark_catalog`)
   - `warehouse_path`: physical path where data will be written
   - `database`: destination database name
   - `table`: name of the target table
   - `mode`: write mode (`overwrite`, `append`, etc.)
   - `partition_by`: list of columns to use for partitioning the data

> Suggestion: Use the jsons in the "examples" folder to test and understand how it works, as well as modify it to adapt to another scenario.


4. ▶️ Execute

Once you've prepared your JSON file, you can run the ingestion process directly via the terminal, providing the path to your spark-jars folder and JSON file:

```bash
python generic_ingestion.py \
  --spark_jars_path /path/to/spark-jars/* \
  --params_json_path /path/to/params.json
```

You can also test more easily how the process works using the **generic_ingestion.ipynb** notebook, running cell by cell.

---

If you want to test each of the JSONs in the "examples" folder, here's what you need:

- **params-api-fakerapi.json**: API availability https://fakerapi.it/api/v1/persons

- **params-api-randomuser.json**: API availability https://randomuser.me/api/

- **params-csv-Crime_Data_from_2020_to_Present.json**: Download the Crime_Data_from_2020_to_Present.csv file (https://data.lacity.org/api/views/2nrs-mtv8/rows.csv?accessType=DOWNLOAD)

- **params-csv-Electric_Vehicle_Population_Data.json**: Download the Electric_Vehicle_Population_Data.csv file (https://data.wa.gov/api/views/f6w7-q2d2/rows.csv?accessType=DOWNLOAD)

- **params-db-Album.json**, **params-db-Artist.json**, **params-db-Playlist.json**: Download the Chinook_Sqlite.sqlite file (https://github.com/lerocha/chinook-database/releases/download/v1.4.5/Chinook_Sqlite.sqlite)
