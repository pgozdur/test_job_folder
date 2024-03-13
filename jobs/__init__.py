from nautobot.apps.jobs import register_jobs
from .my_job import SimpleLogJob
from .import_device_template import AddDeviceTypeJob

register_jobs(SimpleLogJob, AddDeviceTypeJob)