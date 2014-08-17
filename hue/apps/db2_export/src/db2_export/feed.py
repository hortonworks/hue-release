def feed_results(generator, pipe, state, limit, freq=100):
  state.finished_size = 0
  state.finished_rows = 0
  state.set_state("running")
  rc = "success"
  count = 0
  empty = True
  try:
    for row in generator:
      empty = False
      size = len(row)
      if state.finished_size + size + 1 > limit:
        rc = "exceeded"
        break
      pipe.write(row)
      pipe.write("\n")
      state.finished_rows += 1
      state.finished_size += size + 1
      count += 1
      if count % freq == 0: 
        count = 0
        state.save()
    if empty:
       rc = "failed"
  except Exception, e:
    rc = "failed"

  state.set_state(rc)
  state.save()

  return state.finished_size

