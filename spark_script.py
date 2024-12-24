from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, LongType, StringType, DoubleType
from pyspark.sql.functions import from_json, col


spark = SparkSession.builder \
    .appName("Process and Save to Hive and S3") \
    .config("spark.sql.catalogImplementation", "hive") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.access.key", "YOUR_ACCESS_KEY") \
    .config("spark.hadoop.fs.s3a.secret.key", "YOUR_SECRET_KEY") \
    .config("spark.hadoop.fs.s3a.endpoint", "storage.yandexcloud.net") \
    .enableHiveSupport() \
    .getOrCreate()


schema = StructType([
    StructField("time", DoubleType(), True),
    StructField("name", StringType(), True),
    StructField("device_id", LongType(), True),
    StructField("heartrate", DoubleType(), True)
])


input_path = "s3a://bucket-yandex-airflow/df.json"


df = spark.read.text(input_path)


df_parsed = df.withColumn("parsed_value", from_json(col("value"), schema)) \
    .select("parsed_value.*")


df_parsed.write.mode("overwrite").saveAsTable("hive_table")


df_read = spark.sql("SELECT * FROM hive_table")


df_read.show()


transformed_df = df_read.groupBy("name").count()


transformed_df.write.mode("overwrite").saveAsTable("output_table")


output_bucket_path = "s3a://bucket-yandex-airflow/output/"
transformed_df.write.mode("overwrite").csv(output_bucket_path, header=True)

result = spark.sql("SELECT * FROM output_table")
result.show()


spark.stop()
