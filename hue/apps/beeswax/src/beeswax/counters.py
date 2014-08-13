class Counters:

  PATHS = dict(
    HIVE_FILTER_PASSED='counterGroup/counterGroupName=org.apache.hadoop.hive.ql.exec.FilterOperator$Counter/counter/name=PASSED/mapCounterValue',
    MAP_INPUT_RECORDS='counterGroup/counterGroupName=org.apache.hadoop.mapreduce.TaskCounter/counter/name=MAP_INPUT_RECORDS/mapCounterValue',
    REDUCE_INPUT_GROUPS='counterGroup/counterGroupName=org.apache.hadoop.mapreduce.TaskCounter/counter/name=REDUCE_INPUT_GROUPS/reduceCounterValue',
    REDUCE_OUTPUT_RECORDS='counterGroup/counterGroupName=org.apache.hadoop.mapreduce.TaskCounter/counter/name=REDUCE_OUTPUT_RECORDS/reduceCounterValue',
    REDUCE_INPUT_RECORDS='counterGroup/counterGroupName=org.apache.hadoop.mapreduce.TaskCounter/counter/name=REDUCE_INPUT_RECORDS/reduceCounterValue',
    CPU_MILLISECONDS_MAP='counterGroup/counterGroupName=org.apache.hadoop.mapreduce.TaskCounter/counter/name=CPU_MILLISECONDS/mapCounterValue',
    PHYSICAL_MEMORY_SNAPSHOT_MAP='counterGroup/counterGroupName=org.apache.hadoop.mapreduce.TaskCounter/counter/name=PHYSICAL_MEMORY_BYTES/mapCounterValue',
    TOTAL_COMMITTED_HEAP_USAGE_MAP='counterGroup/counterGroupName=org.apache.hadoop.mapreduce.TaskCounter/counter/name=COMMITTED_HEAP_BYTES/mapCounterValue',
    VIRTUAL_MEMORY_SNAPSHOT_MAP='counterGroup/counterGroupName=org.apache.hadoop.mapreduce.TaskCounter/counter/name=VIRTUAL_MEMORY_BYTES/mapCounterValue',
    CPU_MILLISECONDS_REDUCE='counterGroup/counterGroupName=org.apache.hadoop.mapreduce.TaskCounter/counter/name=CPU_MILLISECONDS/reduceCounterValue',
    PHYSICAL_MEMORY_SNAPSHOT_REDUCE='counterGroup/counterGroupName=org.apache.hadoop.mapreduce.TaskCounter/counter/name=PHYSICAL_MEMORY_BYTES/reduceCounterValue',
    TOTAL_COMMITTED_HEAP_USAGE_REDUCE='counterGroup/counterGroupName=org.apache.hadoop.mapreduce.TaskCounter/counter/name=COMMITTED_HEAP_BYTES/reduceCounterValue',
    VIRTUAL_MEMORY_SNAPSHOT_REDUCE='counterGroup/counterGroupName=org.apache.hadoop.mapreduce.TaskCounter/counter/name=VIRTUAL_MEMORY_BYTES/reduceCounterValue',
    )

  def __init__(self, counters):
    self.counters = counters

  def __getitem__(self, key):
    return self._counter(self.PATHS[key.upper()])

  def _counter(self, path):
    """
    Traverse the counter hierachy to get the counter
    """
    value = self.counters
    keys = path.split("/")
    for k in keys:
      if "=" in k:
        # iterate over list and find item
        findkey, findval = k.split("=")
        newvalue = None
        for list_item in value:
          if not list_item.has_key(findkey):
            continue
          if list_item[findkey] == findval:
            newvalue = list_item
            break
        if not newvalue:
          return None
        value = newvalue
      else:
        # get dict value
        if not value.has_key(k):
          return None
        value = value[k]
    return value
