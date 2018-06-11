# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class FormFactor(models.Model):
    form_factor_id = models.AutoField(primary_key=True)
    form_factor_name = models.CharField(db_column='Form_factor_name', max_length=45)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Form_factor'


class HddModels(models.Model):
    hdd_models_id = models.AutoField(primary_key=True)
    hdd_models_name = models.CharField(max_length=60)

    class Meta:
        managed = False
        db_table = 'Hdd_models'


class HddSizes(models.Model):
    hdd_sizes_id = models.AutoField(primary_key=True)
    hdd_sizes_name = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'Hdd_sizes'


class Hdds(models.Model):
    hdd_id = models.AutoField(primary_key=True)
    hdd_serial = models.CharField(max_length=45, blank=True, null=True)
    health = models.IntegerField(blank=True, null=True)
    days_on = models.IntegerField(blank=True, null=True)
    f_lot = models.ForeignKey('Lots', models.DO_NOTHING, blank=True, null=True)
    f_hdd_models = models.ForeignKey(HddModels, models.DO_NOTHING, blank=True, null=True)
    f_hdd_sizes = models.ForeignKey(HddSizes, models.DO_NOTHING, blank=True, null=True)
    f_lock_type = models.ForeignKey('LockType', models.DO_NOTHING, blank=True, null=True)
    f_speed = models.ForeignKey('Speed', models.DO_NOTHING, blank=True, null=True)
    f_form_factor = models.ForeignKey(FormFactor, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Hdds'


class LockType(models.Model):
    lock_type_id = models.AutoField(primary_key=True)
    lock_type_name = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'Lock_type'


class Lots(models.Model):
    lot_id = models.AutoField(primary_key=True)
    lot_name = models.CharField(max_length=45)
    date_of_lot = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Lots'


class Speed(models.Model):
    speed_id = models.AutoField(primary_key=True)
    speed_name = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'Speed'
