# from models import FormFactor, HddModels, HddSizes, Hdds, LockType, Lots, Speed
from hdd_server.models import *
from django.utils import timezone
from django.conf import settings


class HddWriter:

    def __init__(self, file):
        self.file = file

    def save(self):
        self._save_and_set_lots()
        lines_array = self._get_lines_array()
        for line in lines_array:
            line_array = line.split('@')

            model = self._save_and_get_models(line_array[2])
            size = self._save_and_get_size(line_array[3])
            lock_type = self._save_and_get_lock_type(line_array[4])
            speed = self._save_and_get_speed(line_array[5])
            form_factor = self._save_and_get_form_factor(line_array[6])
            self._save_hdd(line_array, model, size, lock_type, speed, form_factor)

    def _save_hdd(self, line_array, model, size, lock_type, speed, form_factor):
        hdd_exists = Hdds.objects.filter(hdd_serial=line_array[1], f_hdd_models=model).exists()
        print(hdd_exists)
        hdd = Hdds(
            hdd_serial=line_array[1],
            health=line_array[7].replace("%", ""),
            days_on=line_array[8],
            f_lot=self.lot,
            f_hdd_models=model,
            f_hdd_sizes=size,
            f_lock_type=lock_type,
            f_speed=speed,
            f_form_factor=form_factor
        )
        hdd.save()

    def _get_lines_array(self):
        content = self.file.read()
        content = content.decode("utf-8")
        linesArray = content.split('\n')
        del linesArray[-1]
        return linesArray

    def _save_and_set_lots(self):
        print(timezone.now())
        timezone.activate(settings.TIME_ZONE)
        try:
            print(self.file._name)
            # self.lot = Lots.objects.filter(lot_name=self.file._name)[0]
            self.lot = Lots.objects.get(lot_name=self.file._name)
        except Lots.DoesNotExist:
            self.lot = Lots(
                lot_name=self.file._name,
                date_of_lot=timezone.now().today().date()
            )
            self.lot.save()

    def _save_and_get_models(self, model):
        model_to_return = HddModels.objects.get_or_create(hdd_models_name=model)[0]
        return model_to_return

    def _save_and_get_size(self, size):
        size_to_return = HddSizes.objects.get_or_create(hdd_sizes_name=size)[0]
        return size_to_return

    def _save_and_get_lock_type(self, lock):
        lock_to_return = LockType.objects.get_or_create(lock_type_name=lock)[0]
        return lock_to_return

    def _save_and_get_speed(self, speed):
        speed_to_return = Speed.objects.get_or_create(speed_name=speed)[0]
        return speed_to_return

    def _save_and_get_form_factor(self, form_factor):
        form_factor_to_return = FormFactor.objects.get_or_create(form_factor_name=form_factor)[0]
        return form_factor_to_return

