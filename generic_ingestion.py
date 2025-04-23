import argparse
import json
import yaml

from pyspark.sql import SparkSession
from pyspark.sql.functions import *


def main():

  APPNAME = "Generic Data Ingestion Script"

  ### GET PARAMETERS
  parser = argparse.ArgumentParser(description = APPNAME)
  parser.add_argument(
    "--spark_jars_path",
    type = str,
    required = True,
    help = "Path to extra Spark JARs (e.g., JDBC drivers)",
  )
  parser.add_argument(
    "--params_json_path",
    type = str,
    required = True,
    help = "Path to the parameters JSON file",
  )

  args = parser.parse_args()

  # Path for spark-jars folder
  SPARK_JARS_PATH = args.spark_jars_path

  # JSON Parameters file
  PARAMS_PATH = args.params_json_path


  # Getting parameters
  with open(PARAMS_PATH, "r") as f:
    params = json.load(f)

  print("\nParameters:\n")
  print(yaml.dump(params, allow_unicode = True, default_flow_style = False, sort_keys = False))


  # SparkSession
  spark = SparkSession.builder \
    .appName("Generic Ingestion") \
    .master("local[*]") \
    .config("spark.sql.session.timeZone", "UTC") \
    .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.4_2.12:1.4.2") \
    .config("spark.jars", SPARK_JARS_PATH) \
    .getOrCreate()

  ### READING DATA
  print("\nReading data ...\n")
  print(yaml.dump(params['source'], allow_unicode = True, default_flow_style = False, sort_keys = False))

  # Source [CSV]
  if params['source']['type'] == "csv":
    print("\nReading CSV file ...")

    df = spark.read.csv(
        path = params['source']['path'],
        sep = params['source']['separator'],
        encoding = params['source']['encoding'],
        header = params['source']['header'],
        inferSchema = True
      )

  # Source [Banco de Dados]
  elif params['source']['type'] == "database":
    print("\nReading database ...")
    QUERY = eval(f'f"{" ".join(params['source']['query']).strip()}"')
    print(QUERY)

    df = spark.read.format("jdbc") \
      .option("driver", params['source']['jdbc_driver']) \
      .option("url", params['source']['url']) \
      .option("dbtable", f"({QUERY})") \
      .option("user", params['source']['user']) \
      .option("password", params['source']['password']) \
      .option("sessionInitStatement", params['source']['execute_before_query']) \
      .load()

  # Source [API]
  elif params['source']['type'] == "api":
    import requests
    import pandas as pd
    print("\nReading api ...")

    response = requests.get(
      params['source']['url'],
      **params['source']['optional_params']
    )

    if params['source']['data_location_key']:
      df_pd = pd.json_normalize(response.json()[params['source']['data_location_key']])
    else:
      df_pd = pd.json_normalize(response.json())

    df = spark.createDataFrame(df_pd)

  df.cache()
  df.show(10)
  df.printSchema()


  ### BASIC DATA TRANSFORMATIONS
  # Rename columns
  df = df.withColumnsRenamed(params["data"]["rename"])

  for col_name in df.columns:
    df = df.withColumnRenamed(col_name, col_name.lower())

  df.printSchema()

  # Trim
  if params['data']['auto_trim']:
    for column in df.columns:
      if dict(df.dtypes)[column] == "string":
        df = df.withColumn(column, trim(df[column]))

  # Pre treatment
  for treat_column_name, treat_column_value in params['data']['treat_columns'].items():
    df = df.withColumn(treat_column_name, expr(treat_column_value))

  # Cast
  for col_cast in params['data']['schema']:
    df = df \
      .withColumn(col_cast['col'], col(col_cast['col']).cast(col_cast['type'])) \
      .withMetadata(col_cast['col'], {'comment': col_cast['comment']})

  df.show(10)

  # Add Python Columns
  for py_column in params['data']['py_columns']:
    df = df \
      .withColumn(py_column['col'], expr(py_column['value'])) \
      .withMetadata(py_column['col'], {'comment': py_column['comment']})


  for field in df.schema.fields:
    print(f"Coluna: {field.name}, Tipo: {field.dataType}, Comentário: {field.metadata.get('comment', 'Nenhum comentário')}")


  ### SAVING DATA
  print("\nSaving data ...\n")
  print(yaml.dump(params['destination'], allow_unicode = True, default_flow_style = False, sort_keys = False))

  catalog = params['destination']['catalog']
  warehouse = params['destination']['warehouse_path']

  spark.conf.set(f"spark.sql.catalog.{catalog}", "org.apache.iceberg.spark.SparkCatalog")
  spark.conf.set(f"spark.sql.catalog.{catalog}.type", "hadoop")
  spark.conf.set(f"spark.sql.catalog.{catalog}.warehouse", warehouse)

  df.write \
    .format("iceberg") \
    .mode(params['destination'].get("mode", "overwrite")) \
    .partitionBy(*params['destination'].get("partition_by", [])) \
    .saveAsTable(f"{params['destination']['catalog']}.{params['destination']['database']}.{params['destination']['table']}")


  spark.read.table(f"{params['destination']['catalog']}.{params['destination']['database']}.{params['destination']['table']}").show()

if __name__ == "__main__":
  main()
