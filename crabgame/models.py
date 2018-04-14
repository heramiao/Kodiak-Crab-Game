from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
import datetime
import os

# Create your models here.
class Crab(models.Model):
    sample_num = models.IntegerField(default = 0)
    done_oocytes = models.IntegerField(default = 0, validators = [MaxValueValidator(10)])
    year = models.IntegerField(default = datetime.date.today().year)
    longitude = models.FloatField()
    latitude = models.FloatField()
    water_temp = models.FloatField() 

    def __str__(self):
        return str((self.sample_num, self.done_oocytes, self.year, self.longitude, self.latitude, self.water_temp))

    # method to increment the crab's done_oocyte once chosen_count reaches desired accuracy --> if conditional

    # method to stop displaying the crab to users once done_oocytes reaches 10 

    # if done_oocytes reaches 10, method to delete all instances of Oocytes that do not have chosen_count 10

def get_upload_path(instance, filename):
    return '{0}/{1}'.format(instance.crab.sample_num, filename)

class Image(models.Model):
    crab = models.ForeignKey(Crab, on_delete = models.CASCADE) # when crab is deleted, images are deleted
    original_img = models.ImageField(upload_to=get_upload_path)
    binarized_img = models.ImageField(upload_to=get_upload_path)
    csv = models.CharField(max_length = 100)

class Oocyte(models.Model):
    crab = models.ForeignKey(Crab, on_delete = models.CASCADE)
    image = models.ForeignKey(Image, on_delete = models.CASCADE)
    chosen_count = models.IntegerField(default = 0) # how many times an oocyte has been clicked by others
    area = models.IntegerField()
    center_x = models.FloatField()
    center_y = models.FloatField()

    # method to increment chosen_count each time somebody clicks on a particular oocyte

    # method to call Crab model to increment done_oocyte once chosen_count reaches desired accuracy 

    # method to check if done_oocyte already incremented once for this instance of Oocyte, 
    # then increment chosen_count but not done_oocyte


class PlaySession(models.Model):
    num_photos = models.IntegerField(default = 10) # assume 10 photos per game session for now
    completed_photos = models.IntegerField(default = 0)

    # method to end PlaySession when completed_photos is incremented to equal num_photos

    # method to increment completed_photos 

class SchoolClass(models.Model):
    className = models.CharField(max_length = 100)

class Intermediate(models.Model):
    oocyte = models.ForeignKey(Oocyte, on_delete = models.CASCADE)
    session = models.ForeignKey(PlaySession, on_delete = models.CASCADE) # need to fix later!!!!
    schoolClass = models.ForeignKey(SchoolClass, on_delete = models.CASCADE)


from django.dispatch import receiver

@receiver(models.signals.post_delete, sender=Image)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.original_img:
        if os.path.isfile(instance.original_img.path):
            os.remove(instance.original_img.path)
            os.remove(instance.binarized_img.path)

@receiver(models.signals.pre_save, sender=Image)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file1 = Image.objects.get(pk=instance.pk).original_img
        old_file2 = Image.objects.get(pk=instance.pk).binarized_img
    except Image.DoesNotExist:
        return False

    new_file1 = instance.original_img
    if not (old_file1 == new_file1):
        if os.path.isfile(old_file1.path):
            os.remove(old_file1.path)
            os.remove(old_file2.path)


