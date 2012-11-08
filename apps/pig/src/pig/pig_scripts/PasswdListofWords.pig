A = load '/tmp/passwd' using PigStorage(',') as (number:int, word:chararray);
B = FOREACH A GENERATE number;
DUMP B;