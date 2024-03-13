from nautobot.extras.jobs import Job, StringVar

class SimpleLogJob(Job):
   class Meta:
       name = "Simple Log Message"
       description = "Logs a simple message to the job output."

   message = StringVar(
       description="This is me doing code "
   )

   def run(self,**kwargs):
       self.logger.info(str(kwargs))
       return kwargs
   