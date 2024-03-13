from nautobot.extras.jobs import Job, FileVar
from nautobot.dcim.models import DeviceType, Manufacturer, InterfaceTemplate
from django.db import transaction
import yaml

class AddDeviceTypeJob(Job):
    """
    Job to add a Device Type from a provided YAML file.
    """

    yaml_file = FileVar(description="YAML file containing device type information")

    def process_yaml(self, yaml_content):
        """
        Process the YAML content and add the device type to Nautobot.
        """

        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            self.logger.error(f"Failed to load YAML data: {str(e)}")
            return

        required_keys = ['manufacturer', 'model', 'part_number', 'u_height', 'is_full_depth']
        if not all(key in data for key in required_keys):
            self.logger.error("YAML data missing one or more required keys: " + ", ".join(required_keys))
            return

        manufacturer, _ = Manufacturer.objects.get_or_create(name=data['manufacturer'])
        device_type, created = DeviceType.objects.get_or_create(
            model=data['model'],
            defaults={
                'manufacturer': manufacturer,
                'part_number': data['part_number'],
                'u_height': data['u_height'],
                'is_full_depth': data['is_full_depth'],
                'subdevice_role': data.get('subdevice_role', ''),
                'comments': data.get('comments', ''),
            }
        )

        if created:
            self.logger.info(f"Device type '{device_type.model}' successfully added.")
        else:
            self.logger.info(f"Device type '{device_type.model}' already exists. Updating details.")
            # Update existing DeviceType with new details
            DeviceType.objects.filter(pk=device_type.pk).update(
                part_number=data['part_number'],
                u_height=data['u_height'],
                is_full_depth=data['is_full_depth'],
                subdevice_role=data.get('subdevice_role', ''),
                comments=data.get('comments', ''),
            )

        # Process interfaces
        for interface in data.get('interfaces', []):
            InterfaceTemplate.objects.update_or_create(
                device_type=device_type,
                name=interface['name'],
                defaults={
                    'type': interface['type'],
                    'mgmt_only': interface.get('mgmt_only', False),
                }
            )

    @transaction.atomic
    def run(self, yaml_file):
        """
        The main entry point for the Job, with transaction handling.
        """
        self.process_yaml(yaml_file.read())
