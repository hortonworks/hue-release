#!/bin/sh  


nc -z localhost 8000 < /dev/null 
SANDBOX_EXIT_CODE=$?                                               
 
if [[ SANDBOX_EXIT_CODE != 0 ]]; then                                                            
  echo "Sandbox is not running";                                              
fi

nc -z localhost 8002 < /dev/null 
SANDBOX_EXIT_CODE &= $?                                               
 
if [[ SANDBOX_EXIT_CODE != 0 ]]; then                                                            
  echo "Beeswax is not running";                                              
fi

exit $SANDBOX_EXIT_CODE