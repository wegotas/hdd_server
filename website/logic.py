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
            lock_state = self._save_and_get_lock_state(line_array[4])
            speed = self._save_and_get_speed(line_array[5])
            form_factor = self._save_and_get_form_factor(line_array[6])
            self._save_hdd(line_array, model, size, lock_state, speed, form_factor)

    def _save_hdd(self, line_array, model, size, lock_state, speed, form_factor):
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
                f_lock_state=lock_state,
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
                f_lock_state=lock_state,
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

    def _save_and_get_lock_state(self, lock):
        lock_to_return = LockState.objects.get_or_create(lock_state_name=lock)[0]
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


class LotHolder:

    def __init__(self, lot_id, lot_name, date_of_lot, count):
        self.lot_id = lot_id
        self.lot_name = lot_name
        self.date_of_lot = date_of_lot
        self.count = count


class LotsHolderAutoFilter:

    def __init__(self, lots):
        self.lots_names = []
        self.dates_of_lots = []
        self.counts = []
        for lot in lots:
            self.lots_names.append(lot.lot_name)
            self.dates_of_lots.append(lot.date_of_lot)
            self.counts.append(lot.count)
        self.lots_names = list(set(self.lots_names))
        self.lots_names.sort()
        self.dates_of_lots = list(set(self.dates_of_lots))
        self.dates_of_lots.sort()
        self.counts = list(set(self.counts))
        self.counts.sort()


class LotsHolder:

    def __init__(self):
        self.lots = self._get_lots()
        self.autoFilters = LotsHolderAutoFilter(self.lots)


    def _get_lots(self):
        lots = Lots.objects.all()
        lots_to_return = []
        for lot in lots:
            count = Hdds.objects.filter(f_lot=lot.lot_id).count()
            lh = LotHolder(lot.lot_id, lot.lot_name, lot.date_of_lot, count)
            lots_to_return.append(lh)
        return lots_to_return

    def filter(self, data_dict):
        keys = ('nam-af', 'dat-af', 'cnt-af')
        new_dict = {}
        if 'lots' in data_dict:
            data_dict.pop('lots')
        for key in keys:
            if key in data_dict:
                new_dict[key] = data_dict.pop(key)
        print(new_dict)
        '''
        for key, value in new_dict.items():
            if key == '':
        '''


class HddHolder:

    def __init__(self):
        self.hdds = Hdds.objects.all()
        self.autoFilters = HddAutoFilterOptions(self.hdds)

    def filter(self, data_dict):
        keys = ('ser-af', 'mod-af', 'siz-af', 'loc-af', 'spe-af', 'for-af', 'hp-af', 'day-af')
        new_dict = {}
        if 'hdds' in data_dict:
            data_dict.pop('hdds')
        for key in keys:
            if key in data_dict:
                new_dict[key] = data_dict.pop(key)
        for key, value in new_dict.items():
            if key in keys:
                if key == 'ser-af':
                    self.hdds = self.hdds.filter(hdd_serial__in=new_dict[key])
                elif key == 'mod-af':
                    self.hdds = self.hdds.filter(f_hdd_models__hdd_models_name__in=new_dict[key])
                elif key == 'siz-af':
                    self.hdds = self.hdds.filter(f_hdd_sizes__hdd_sizes_name__in=new_dict[key])
                elif key == 'loc-af':
                    self.hdds = self.hdds.filter(f_lock_state__lock_state_name__in=new_dict[key])
                elif key == 'spe-af':
                    self.hdds = self.hdds.filter(f_speed__speed_name__in=new_dict[key])
                elif key == 'for-af':
                    self.hdds = self.hdds.filter(f_form_factor__form_factor_name__in=new_dict[key])
                elif key == 'hp-af':
                    self.hdds = self.hdds.filter(health__in=new_dict[key])
                elif key == 'day-af':
                    self.hdds = self.hdds.filter(days_on__in=new_dict[key])


class HddAutoFilterOptions:

    def __init__(self, hdds):
        self._get_serials(hdds)
        self._get_models(hdds)
        self._get_sizes(hdds)
        self._get_locks(hdds)
        self._get_speeds(hdds)
        self._get_forms(hdds)
        self._get_healths(hdds)
        self._get_days(hdds)

    def _get_serials(self, hdds):
        serials = hdds.values('hdd_serial').distinct()
        self.serials = [a['hdd_serial'] for a in serials]
        self.serials.sort()

    def _get_models(self, hdds):
        f_models = hdds.values('f_hdd_models').distinct()
        models_ids = [a['f_hdd_models'] for a in f_models]
        self.models = []
        for id in models_ids:
            if id is None:
                self.models.append('')
            else:
                model = HddModels.objects.get(hdd_models_id=id)
                self.models.append(model.hdd_models_name)
        self.models = list(set(self.models))
        self.models.sort()

    def _get_sizes(self, hdds):
        f_sizes = hdds.values('f_hdd_sizes').distinct()
        sizes_ids = [a['f_hdd_sizes'] for a in f_sizes]
        self.sizes = []
        for id in sizes_ids:
            if id is None:
                self.sizes.append('')
            else:
                size = HddSizes.objects.get(hdd_sizes_id=id)
                self.sizes.append(size.hdd_sizes_name)
        self.sizes = list(set(self.sizes))
        self.sizes.sort()

    def _get_locks(self, hdds):
        f_locks = hdds.values('f_lock_state').distinct()
        locks_ids = [a['f_lock_state'] for a in f_locks]
        self.locks = []
        for id in locks_ids:
            if id is None:
                self.sizes.append('')
            else:
                lock = LockState.objects.get(lock_state_id=id)
                self.locks.append(lock.lock_state_name)
        self.locks = list(set(self.locks))
        self.locks.sort()

    def _get_speeds(self, hdds):
        f_speeds = hdds.values('f_speed').distinct()
        speeds_ids = [a['f_speed'] for a in f_speeds]
        self.speeds = []
        for id in speeds_ids:
            if id is None:
                self.speeds.append('')
            else:
                speed = Speed.objects.get(speed_id=id)
                self.speeds.append(speed.speed_name)
        self.speeds = list(set(self.speeds))
        self.speeds.sort()

    def _get_forms(self, hdds):
        f_forms = hdds.values('f_form_factor').distinct()
        forms_ids = [a['f_form_factor'] for a in f_forms]
        self.forms = []
        for id in forms_ids:
            if id is None:
                self.forms.append('')
            else:
                formfactor = FormFactor.objects.get(form_factor_id=id)
                self.forms.append(formfactor.form_factor_name)
        self.forms = list(set(self.forms))
        self.forms.sort()

    def _get_healths(self, hdds):
        healths = hdds.values('health').distinct()
        self.healths = [a['health'] for a in healths]
        self.healths.sort()

    def _get_days(self, hdds):
        days = hdds.values('days_on').distinct()
        self.days = [a['days_on'] for a in days]
        self.days.sort()


class LotContentHolder:

    def __init__(self, index):
        self.lot = Lots.objects.get(lot_id=index)
        self.hdds = Hdds.objects.filter(f_lot=self.lot)