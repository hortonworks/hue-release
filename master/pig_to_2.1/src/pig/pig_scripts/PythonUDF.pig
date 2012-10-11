REGISTER /home/hue/test.py using jython as myfuncs;
A = load '/tmp/passwd' using PigStorage(',') as (number:int, word:chararray);
B = FOREACH A GENERATE myfuncs.helloworld(), myfuncs.square(3);
DUMP B;