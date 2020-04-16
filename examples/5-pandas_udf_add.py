from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, DataTypes
from pyflink.table.descriptors import Schema, OldCsv, FileSystem
from pyflink.table.udf import udf

# Init environment
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)
t_env = StreamTableEnvironment.create(env)

# Define and register UDF
add = udf(lambda i, j: i + j, [DataTypes.BIGINT(), DataTypes.BIGINT()], DataTypes.BIGINT(), udf_type="pandas")
t_env.register_function("add", add)

# Register Source
t_env.connect(FileSystem().path('/opt/examples/data/udf_add_input')) \
    .with_format(OldCsv()
                 .field('a', DataTypes.BIGINT())
                 .field('b', DataTypes.BIGINT())) \
    .with_schema(Schema()
                 .field('a', DataTypes.BIGINT())
                 .field('b', DataTypes.BIGINT())) \
    .create_temporary_table('mySource')

# Register Sink
t_env.connect(FileSystem().path('/opt/examples/data/udf_add_output')) \
    .with_format(OldCsv()
                 .field('sum', DataTypes.BIGINT())) \
    .with_schema(Schema()
                 .field('sum', DataTypes.BIGINT())) \
    .create_temporary_table('mySink')

# Query
t_env.from_path('mySource')\
    .select("add(a, b)") \
    .insert_into('mySink')

t_env.execute("5-pandas_udf_add")