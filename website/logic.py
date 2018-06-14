from hdd_server.models import *
from django.utils import timezone
from django.conf import settings
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import logging
import os
from threading import Thread


class HddWriter:

    def __init__(self, file, filename):
        self.file = file
        self.filename = filename

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
        if Hdds.objects.filter(hdd_serial=line_array[1], f_hdd_models=model).exists():
            logging.debug("Such hdd allready exists")
            existing_hdd = Hdds.objects.get(hdd_serial=line_array[1], f_hdd_models=model)
            logging.debug(existing_hdd)
            logging.debug(existing_hdd.__dict__)
            hdd = Hdds(
                hdd_id=existing_hdd.hdd_id,
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
        else:
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
        try:
            content = content.decode("utf-8")
        except AttributeError:
            pass
        linesArray = content.split('\n')
        del linesArray[-1]
        return linesArray

    def _save_and_set_lots(self):
        try:
            self.lot = Lots.objects.get(lot_name=self.filename)
        except Lots.DoesNotExist:
            self.lot = Lots(
                lot_name=self.filename,
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


class MyHandler(PatternMatchingEventHandler):
    patterns = ['*']

    def process(self, event):
        logging.debug(event.src_path)
        logging.debug(event.event_type)
        index = 0
        with open(event.src_path) as file:
            hw = HddWriter(file, 'test')
            hw.save()
        logging.debug(index)
        logging.debug('_________________________________________')

    def on_created(self, event):
        if not event.is_directory:
            self.process(event)


def start_observer():
    observer = Observer()
    logging.basicConfig(filename='observer.log', level=logging.DEBUG, format="%(threadName)s:%(message)s")
    observer.schedule(MyHandler(), '/home/sopenaclient/Desktop/django_project/hdd_server/media')
    logging.debug("Start of observer")
    observer.start()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logging.debug('Ending observer, due to keyboard interupt')
        observer.stop()
        logging.debug('Observerer ended')
    observer.join()


def on_start():
    print("on start")
    """
    if os.environ['RUN_ON_START']:
        os.environ['RUN_ON_START'] = 'False'
        tid = Thread(target=start_observer)
        tid.start()
    """