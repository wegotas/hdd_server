from hdd_server.models import *
from django.utils import timezone
from django.conf import settings
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import logging
import os
from threading import Thread
import tarfile
import datetime
from subprocess import call


def on_start():
    print("on start")
    if os.environ['RUN_ON_START']:
        os.environ['RUN_ON_START'] = 'False'
        tarThread = Thread(target=start_tar_observer)
        tarThread.start()
        txtThread = Thread(target=start_txt_observer)
        txtThread.start()


def start_tar_observer():
    observer = Observer()
    log_position = os.path.join(os.path.join(settings.BASE_DIR, 'logs'), 'observer.log')
    logging.basicConfig(filename=log_position, level=logging.DEBUG, format="%(asctime)-15s %(threadName)s:%(message)s")
    observer.schedule(TarAndLogHandler(), os.path.join(os.path.join(settings.BASE_DIR, 'temp')))
    logging.debug("Start of tar observer")
    observer.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logging.debug('Ending observer, due to keyboard interupt')
        observer.stop()
        logging.debug('Observer ended')
    observer.join()


class TarAndLogHandler(PatternMatchingEventHandler):
    patterns = ['*.tar']

    def process(self, event):
        logging.debug(event.src_path)
        logging.debug(event.event_type)
        index = 0
        tp = TarProcessor(event.src_path, os.path.basename(event.src_path).replace('.tar', ''))
        tp.process_data()
        logging.debug(index)
        logging.debug('_________________________________________')

    def on_created(self, event):
        if not event.is_directory:
            self.process(event)


def start_txt_observer():
    observer = Observer()
    log_position = os.path.join(os.path.join(settings.BASE_DIR, 'logs'), 'observer.log')
    logging.basicConfig(filename=log_position, level=logging.DEBUG, format="%(asctime)-15s %(threadName)s:%(message)s")
    observer.schedule(TxtAndLogHandler(), os.path.join(os.path.join(settings.BASE_DIR, 'temp')))
    logging.debug("Start of txt observer")
    observer.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logging.debug('Ending observer, due to keyboard interupt')
        observer.stop()
        logging.debug('Observer ended')
    observer.join()


class TxtAndLogHandler(PatternMatchingEventHandler):
    patterns = ['*.txt']

    def process(self, event):
        logging.debug(event.src_path)
        logging.debug(event.event_type)
        index = 0
        # WIP, NEED FINISHING
        hop = HddOrderProcessor(event.src_path)
        logging.debug(index)
        logging.debug('_________________________________________')

    def on_created(self, event):
        if not event.is_directory:
            self.process(event)


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
        self.count = 0
        self.lots = self._get_lots()
        self.autoFilters = LotsHolderAutoFilter(self.lots)

    def increment(self):
        self.count += 1
        return ''

    def _get_lots(self):
        lots = Lots.objects.all()
        lots_to_return = []
        for lot in lots:
            count = Hdds.objects.filter(f_lot=lot.lot_id).count()
            lh = LotHolder(lot.lot_id, lot.lot_name, lot.date_of_lot, count)
            lots_to_return.append(lh)
        return lots_to_return

    def filter(self, data_dict):
        keys = ('nam-af', 'day-af', 'cnt-af')
        new_dict = {}
        if 'lots' in data_dict:
            data_dict.pop('lots')
        for key in keys:
            if key in data_dict:
                new_dict[key] = data_dict.pop(key)
        for key, value in new_dict.items():
            if key == 'nam-af':
                for lot in self.lots[:]:
                    if not lot.lot_name in new_dict[key]:
                        self.lots.remove(lot)
            elif key == 'day-af':
                for lot in self.lots[:]:
                    if not str(lot.date_of_lot) in new_dict[key]:
                        self.lots.remove(lot)
            elif key == 'cnt-af':
                for lot in self.lots[:]:
                    if not str(lot.count) in new_dict[key]:
                        self.lots.remove(lot)


class HddHolder:

    def __init__(self):
        self.count = 0
        self.hdds = Hdds.objects.all()
        self.autoFilters = HddAutoFilterOptions(self.hdds)
        self.changedKeys = []

    def increment(self):
        self.count += 1
        return ''

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
                self.changedKeys.append(key)
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
        self.autoFilters = HddAutoFilterOptions(self.hdds)


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
        self.autoFilters = HddAutoFilterOptions(self.hdds)
        self.changedKeys = []

    def filter(self, data_dict):
        # print(data_dict)
        keys = ('siz-af', 'loc-af', 'day-af', 'for-af', 'spe-af', 'mod-af', 'hp-af', 'ser-af')
        new_dict = {}
        for key in keys:
            if key in data_dict:
                new_dict[key] = data_dict.pop(key)
        # print(new_dict)
        for key, value in new_dict.items():
            # print(key + ' ' + str(value))
            self.changedKeys.append(key)
            if key == 'siz-af':
                self.hdds = self.hdds.filter(f_hdd_sizes__hdd_sizes_name__in=new_dict[key])
            elif key == 'loc-af':
                self.hdds = self.hdds.filter(f_lock_state__lock_state_name__in=new_dict[key])
            elif key == 'day-af':
                self.hdds = self.hdds.filter(days_on__in=new_dict[key])
            elif key == 'for-af':
                self.hdds = self.hdds.filter(f_form_factor__form_factor_name__in=new_dict[key])
            elif key == 'spe-af':
                self.hdds = self.hdds.filter(f_speed__speed_name__in=new_dict[key])
            elif key == 'mod-af':
                self.hdds = self.hdds.filter(f_hdd_models__hdd_models_name__in=new_dict[key])
            elif key == 'hp-af':
                self.hdds = self.hdds.filter(health__in=new_dict[key])
            elif key == 'ser-af':
                self.hdds = self.hdds.filter(hdd_serial__in=new_dict[key])
            self.autoFilters = HddAutoFilterOptions(self.hdds)


class HddOrderToDelete:

    def __init__(self, index):
        self.message = ''
        self.order = HddOrder.objects.get(order_id=index)
        self.hdds = Hdds.objects.filter(f_order=self.order)

    def delete(self):
        self.hdds.update(f_order=None)
        self.order.delete()


class HddOrderContentHolder:

    def __init__(self, index):
        self.hdd_order = HddOrder.objects.get(order_id=index)
        self.hdds = Hdds.objects.filter(f_order=self.hdd_order)
        self.autoFilters = HddAutoFilterOptions(self.hdds)
        self.changedKeys = []

    def filter(self, data_dict):
        # print(data_dict)
        keys = ('siz-af', 'loc-af', 'day-af', 'for-af', 'spe-af', 'mod-af', 'hp-af', 'ser-af')
        new_dict = {}
        for key in keys:
            if key in data_dict:
                new_dict[key] = data_dict.pop(key)
        # print(new_dict)
        for key, value in new_dict.items():
            # print(key + ' ' + str(value))
            self.changedKeys.append(key)
            if key == 'siz-af':
                self.hdds = self.hdds.filter(f_hdd_sizes__hdd_sizes_name__in=new_dict[key])
            elif key == 'loc-af':
                self.hdds = self.hdds.filter(f_lock_state__lock_state_name__in=new_dict[key])
            elif key == 'day-af':
                self.hdds = self.hdds.filter(days_on__in=new_dict[key])
            elif key == 'for-af':
                self.hdds = self.hdds.filter(f_form_factor__form_factor_name__in=new_dict[key])
            elif key == 'spe-af':
                self.hdds = self.hdds.filter(f_speed__speed_name__in=new_dict[key])
            elif key == 'mod-af':
                self.hdds = self.hdds.filter(f_hdd_models__hdd_models_name__in=new_dict[key])
            elif key == 'hp-af':
                self.hdds = self.hdds.filter(health__in=new_dict[key])
            elif key == 'ser-af':
                self.hdds = self.hdds.filter(hdd_serial__in=new_dict[key])
            self.autoFilters = HddAutoFilterOptions(self.hdds)


class HddToEdit:

    def __init__(self, index):
        self.hdd = Hdds.objects.get(hdd_id=index)
        self.get_sizes()
        self.get_states()
        self.get_speeds()
        self.get_form_factors()

    def get_sizes(self):
        self.sizes = [record[0] for record in HddSizes.objects.values_list('hdd_sizes_name')]
        self.sizes.sort()

    def get_states(self):
        self.states = [record[0] for record in LockState.objects.values_list('lock_state_name')]
        self.sizes.sort()

    def get_speeds(self):
        self.speeds = [record[0] for record in Speed.objects.values_list('speed_name')]
        self.speeds.sort()

    def get_form_factors(self):
        self.form_factors = [record[0] for record in FormFactor.objects.values_list('form_factor_name')]
        self.form_factors.sort()

    def process_edit(self, index, data_dict):
        # print(index)
        model = self.get_or_save_model(data_dict.pop('model')[0])
        size = self.get_or_save_size(data_dict.pop('size')[0])
        state = self.get_or_save_state(data_dict.pop('state')[0])
        speed = self.get_or_save_speed(data_dict.pop('speed')[0])
        form_factor = self.get_or_save_form_factor(data_dict.pop('form_factor')[0])
        hdd = Hdds.objects.get(hdd_id=index)
        hdd.hdd_serial = data_dict.pop('serial')[0]
        hdd.health = data_dict.pop('health')[0]
        hdd.days_on = data_dict.pop('days')[0]
        hdd.f_hdd_models = model
        hdd.f_hdd_sizes = size
        hdd.f_lock_state = state
        hdd.f_speed = speed
        hdd.f_form_factor = form_factor
        hdd.save()

    def get_or_save_model(self, model_text):
        model = HddModels.objects.get_or_create(hdd_models_name=model_text)[0]
        return model

    def get_or_save_size(self, size_text):
        size = HddSizes.objects.get_or_create(hdd_sizes_name=size_text)[0]
        return size

    def get_or_save_state(self, state_text):
        state = LockState.objects.get_or_create(lock_state_name=state_text)[0]
        return state

    def get_or_save_speed(self, speed_text):
        speed = Speed.objects.get_or_create(speed_name=speed_text)[0]
        return speed

    def get_or_save_form_factor(self, form_factor_text):
        form_factor = FormFactor.objects.get_or_create(form_factor_name=form_factor_text)[0]
        return form_factor


class HddToDelete:

    def __init__(self, pk=None, serial=None):
        if pk:
            self.hdd = Hdds.objects.filter(hdd_id=pk)[0]
        if serial:
            self.hdd = Hdds.objects.filter(hdd_serial=serial)[0]
        self.success = False
        self.message = ''

    def delete(self):
        try:
            """
            'QuerySet' object has no attribute 'f_lot'
            """
            os.system('tar -vf ' + os.path.join(os.path.join(settings.BASE_DIR, 'tarfiles'), self.hdd.f_lot.lot_name + '.tar') + ' --delete "' + self.hdd.tar_member_name + '"')
            self.hdd.delete()
            self.success = True
            print('Succesful deletion')
        except Exception as e:
            self.success = False
            self.message = 'Failure to delete record\r\n'+str(e)
            print('Failed deletion')


class TarProcessor:

    def __init__(self, inMemoryFile, filename=None):
        if filename is None:
            self.lot_name = inMemoryFile._name.replace('.tar', '')
            self.tar = tarfile.open(fileobj=inMemoryFile.file)
            self.fileLoc = ''
        else:
            self.lot_name = filename.replace('.tar', '')
            self.tar = tarfile.open(inMemoryFile)
            self.fileLoc = filename

    def process_data(self):
        self._save_and_set_lots()
        # print(type(self.tar))
        for member in self.tar.getmembers():
            if '.txt' in member.name:
                file = self.tar.extractfile(member)
                with open(os.path.join(os.path.join(settings.BASE_DIR, 'logs'), 'failed.log'), 'a') as logfile:
                    textToWrite = '* importing lot ' + self.lot_name + ' || ' + str(datetime.date.today()) + ' *\r\n'
                    isMissing = False
                    new_tarfile_loc = os.path.join(os.path.join(settings.BASE_DIR, 'tarfiles'), self.lot_name + '.tar')
                    with tarfile.open(new_tarfile_loc, 'a') as new_tar:
                        for bline in file.readlines():
                            try:
                                line = bline.decode('utf-8')
                                line_array = line.split('@')
                                if self.isValid(line_array):
                                    tarmember = self.get_tar_member_by_serial(line_array)
                                    if self._hdd_exists(line_array):
                                        if tarmember is not None:
                                            isMissing = True
                                            tarmember_to_remove = self.get_tarmember_name(line_array)
                                            if tarmember_to_remove is not None:
                                                print(type(tarmember_to_remove))
                                                tarmember_to_remove = self.get_tarmember_name(line_array)
                                                try:
                                                    new_tar.getmember(tarmember_to_remove)
                                                    os.system('tar -vf '+new_tarfile_loc+' --delete "'+tarmember_to_remove+'"')
                                                    print('After deletion')
                                                except:
                                                    print('File opening or its deletion had failed')
                                                    pass
                                            filename = tarmember.name
                                            file = self.tar.extractfile(tarmember)
                                            new_tar.addfile(tarmember, file)
                                            print('Added tarmember:')
                                            print(tarmember)
                                            self._update_existing_hdd(line_array, filename)
                                            textToWrite += 'SN: ' + line_array[1] + '| info updated. File updated.\r\n'
                                        else:
                                            self._update_existing_hdd_without_file(line_array)
                                            isMissing = True
                                            textToWrite += 'SN: ' + line_array[1] + '| Record info updated. File info not changed.\r\n'
                                    else:
                                        if tarmember is not None:
                                            file = self.tar.extractfile(tarmember)
                                            filename = tarmember.name
                                            new_tar.addfile(tarmember, file)
                                            self._save_new_hdd(line_array, filename)
                                        else:
                                            isMissing = True
                                            textToWrite += 'SN: ' + line_array[1] + '| skipped. Not present in database. No file associated.\r\n'
                                else:
                                    textToWrite += 'SN: ' + line_array[1] + '| values which should be numbers, are not.\r\n'
                            except Exception as e:
                                isMissing = True
                                textToWrite +='\r\n Error: ' + str(e)+' \r\n'
                        textToWrite += '===============================================\r\n'
                        if isMissing:
                            logfile.write(textToWrite)
        try:
            if self.fileLoc != '':
                os.remove(self.fileLoc)
        except:
            pass

    def get_tarmember_name(self, line_array):
        model = HddModels.objects.get_or_create(hdd_models_name=line_array[2])[0]
        hdd = Hdds.objects.filter(hdd_serial=line_array[1], f_hdd_models=model)[0]
        return hdd.tar_member_name

    def get_tar_member_by_serial(self, line_array):
        for member in self.tar.getmembers():
            if '(S-N ' + line_array[1] + ')' in member.name:
                return member
        return None

    def isValid(self, line_array):
        if line_array[7].replace("%", "").strip().isdigit() and line_array[8].strip().isdigit():
            return True
        return False

    def _update_existing_hdd_without_file(self, line_array):
        model = HddModels.objects.get_or_create(hdd_models_name=line_array[2])[0]
        hdd = Hdds.objects.filter(hdd_serial=line_array[1], f_hdd_models=model)[0]
        size = self._save_and_get_size(line_array[3])
        lock_state = self._save_and_get_lock_state(line_array[4])
        speed = self._save_and_get_speed(line_array[5])
        form_factor = self._save_and_get_form_factor(line_array[6])
        hdd.f_hdd_sizes = size
        hdd.f_lock_state = lock_state
        hdd.f_speed = speed
        hdd.f_form_factor = form_factor
        hdd.health = line_array[7].replace("%", "")
        hdd.days_on = line_array[8]
        hdd.f_lot = self.lot
        hdd.save()

    def _update_existing_hdd(self, line_array, filename):
        model = HddModels.objects.get_or_create(hdd_models_name=line_array[2])[0]
        hdd = Hdds.objects.filter(hdd_serial=line_array[1], f_hdd_models=model)[0]
        size = self._save_and_get_size(line_array[3])
        lock_state = self._save_and_get_lock_state(line_array[4])
        speed = self._save_and_get_speed(line_array[5])
        form_factor = self._save_and_get_form_factor(line_array[6])
        hdd.f_hdd_sizes = size
        hdd.f_lock_state = lock_state
        hdd.f_speed = speed
        hdd.f_form_factor = form_factor
        hdd.health = line_array[7].replace("%", "")
        hdd.days_on = line_array[8]
        hdd.tar_member_name = filename
        hdd.f_lot = self.lot
        hdd.save()

    def _save_new_hdd(self, line_array, filename):
        model = self._save_and_get_models(line_array[2])
        size = self._save_and_get_size(line_array[3])
        lock_state = self._save_and_get_lock_state(line_array[4])
        speed = self._save_and_get_speed(line_array[5])
        form_factor = self._save_and_get_form_factor(line_array[6])
        hdd = Hdds(
            hdd_serial=line_array[1],
            health=line_array[7].replace("%", ""),
            days_on=line_array[8],
            tar_member_name=filename,
            f_lot=self.lot,
            f_hdd_models=model,
            f_hdd_sizes=size,
            f_lock_state=lock_state,
            f_speed=speed,
            f_form_factor=form_factor
        )
        hdd.save()

    def _hdd_exists(self, line_array):
        model = HddModels.objects.get_or_create(hdd_models_name=line_array[2])[0]
        hdd = Hdds.objects.filter(hdd_serial=line_array[1], f_hdd_models=model)
        return hdd.exists()

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

    def _save_and_set_lots(self):
        try:
            self.lot = Lots.objects.get(lot_name=self.lot_name)
        except Lots.DoesNotExist:
            self.lot = Lots(
                lot_name=self.lot_name,
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


class PDFViewer:

    def __init__(self, pk):
        self.success = False
        try:
            hdd = Hdds.objects.get(hdd_id=pk)
            tf = tarfile.open(os.path.join(os.path.join(settings.BASE_DIR, 'tarfiles'), hdd.f_lot.lot_name + '.tar'))
            tarmember = tf.getmember(hdd.tar_member_name)
            pdf = tf.extractfile(tarmember)
            pdf_content = pdf.read()
            self.pdf_content = pdf_content
            self.success = True
        except:
            pass


class HddOrderProcessor:

    def __init__(self, txtObject):
        self.message = ''
        print(type(txtObject))
        print(txtObject)
        if type(txtObject) is str:
            filename = os.path.basename(txtObject)
            txtObject = open(txtObject, "r")
        else:
            filename = txtObject._name
        hddOrder = self.get_hdd_order(filename)
        with open(os.path.join(os.path.join(settings.BASE_DIR, 'logs'), 'failed.log'), 'a') as logfile:
            isMissing = False
            textToWrite = '* importing order ' + filename.replace('.txt', '')+ ' || ' + str(datetime.date.today()) + ' *\r\n'
            for line in txtObject.readlines():
                try:
                    line = line.decode('utf-8')
                except:
                    pass
                line_array = line.split('@')
                if self.isValid(line_array):
                    model = HddModels.objects.get_or_create(hdd_models_name=line_array[2])[0]
                    hdds = Hdds.objects.filter(hdd_serial=line_array[1], f_hdd_models=model)
                    if hdds.exists():
                        if hdds[0].f_order is not None:
                            isMissing = True
                            textToWrite += 'SN: ' + hdds[0].hdd_serial + '| had order asign. Was assigned to order ' + hdds[0].f_order.order_name
                        hdds.update(f_order=hddOrder)
                    else:
                        model = HddModels.objects.get_or_create(hdd_models_name=line_array[2])[0]
                        size = HddSizes.objects.get_or_create(hdd_sizes_name=line_array[3])[0]
                        lock_state = LockState.objects.get_or_create(lock_state_name=line_array[4])[0]
                        speed = Speed.objects.get_or_create(speed_name=line_array[5])[0]
                        form_factor = FormFactor.objects.get_or_create(form_factor_name=line_array[6])[0]
                        hdd = Hdds(
                            hdd_serial=line_array[1],
                            health=line_array[7].replace("%", ""),
                            days_on=line_array[8],
                            f_hdd_models=model,
                            f_hdd_sizes=size,
                            f_lock_state=lock_state,
                            f_speed=speed,
                            f_form_factor=form_factor,
                            f_order=hddOrder
                        )
                        hdd.save()
            textToWrite += '===============================================\r\n'
            if isMissing:
                logfile.write(textToWrite)
                self.message = textToWrite

    def isValid(self, line_array):
        if line_array[7].replace("%", "").strip().isdigit() and line_array[8].strip().isdigit():
            return True
        return False

    def get_hdd_order(self, txtFileName):
        hddOrders = HddOrder.objects.filter(order_name=txtFileName.replace('.txt', ''))
        if hddOrders.exists():
            hdds = Hdds.objects.filter(f_order=hddOrders[0].order_id)
            hdds.update(f_order=None)
            hddOrders[0].delete()
        hddOrder = HddOrder(
            order_name=txtFileName.replace('.txt', ''),
            date_of_order=timezone.now().today().date(),
            is_sold=0
        )
        hddOrder.save()
        return hddOrder


class HddOrderHolder:

    def __init__(self, order_id, order_name, date_of_order, is_sold, count):
        self.order_id = order_id
        self.order_name = order_name
        self.date_of_order = date_of_order
        self.is_sold = is_sold
        self.count = count


class HddOrdersHolderAutoFilter:

    def __init__(self, orders):
        self.orders_names = []
        self.dates_of_orders = []
        self.are_sold = []
        self.counts = []
        for order in orders:
            self.orders_names.append(order.order_name)
            self.dates_of_orders.append(order.date_of_order)
            self.are_sold.append(order.is_sold)
            self.counts.append(order.count)
        self.orders_names = list(set(self.orders_names))
        self.orders_names.sort()
        self.dates_of_orders = list(set(self.dates_of_orders))
        self.dates_of_orders.sort()
        self.are_sold = list(set(self.are_sold))
        self.are_sold.sort()
        self.counts = list(set(self.counts))
        self.counts.sort()


class HddOrdersHolder:

    def __init__(self):
        self.count = 0
        self.set_orders()
        self.autoFilters = HddOrdersHolderAutoFilter(self.orders)

    def increment(self):
        self.count += 1
        return ''

    def filter(self, data_dict):
        # print(data_dict)
        keys = ('hon-af', 'dat-af', 'cnt-af')
        new_dict = {}
        for key in keys:
            if key in data_dict:
                new_dict[key] = data_dict.pop(key)
        print(new_dict)
        for key, value in new_dict.items():
            if key == 'hon-af':
                print('It is hon-af')
                for order in self.orders[:]:
                    print(order.order_name)
                    if not order.order_name in new_dict[key]:
                        self.orders.remove(order)
            elif key == 'dat-af':
                print('It is dat-af')
                for order in self.orders[:]:
                    if not str(order.date_of_order) in new_dict[key]:
                        self.orders.remove(order)
            elif key == 'cnt-af':
                print('It is cnt-af')
                for order in self.orders[:]:
                    if not str(order.count) in new_dict[key]:
                        self.orders.remove(order)
        self.autoFilters = HddOrdersHolderAutoFilter(self.orders)

    def set_orders(self):
        orders = HddOrder.objects.all()
        self.orders = []
        for order in orders:
            count = Hdds.objects.filter(f_order=order).count()
            oh = HddOrderHolder(order.order_id, order.order_name, order.date_of_order, order.is_sold, count)
            self.orders.append(oh)