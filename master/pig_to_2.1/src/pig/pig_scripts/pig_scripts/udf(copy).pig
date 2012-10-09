REGISTER hdfs://ip-10-191-121-144.ec2.internal:8020/tmp/udf.jar;
A = load 'passwd' using PigStorage(',') as (number:int, word:chararray);
B = FOREACH A GENERATE udf.UPPER(word);
DUMP B;