def create(request):
  si = StepInfo()
  si.submit = int(request.POST.get(StepInfo.SUBMIT_STEP, 0))
  target = request.POST.get(StepInfo.TARGET_STEP)
  if target == None:
    si.target = None
  else:
    si.target = int(target)
  return si

class StepInfo:

  SUBMIT_STEP = "submit-step"
  TARGET_STEP = "target-step"
