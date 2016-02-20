from django.db import models
from django.contrib.admin import ModelAdmin

LEVELS = (
    ('Beginner', 'Beginner'),
    ('Easy', 'Easy'),
    ('Medium', 'Medium'),
    ('Hard', 'Hard'),
    ('Challenge', 'Expert'),
    ('Edit', 'Edit')
)

STYLES = (
    ('single', 'Single'),
    ('double', 'Double'),
    ('routine', 'Routine')
)


class StepchartAdmin(ModelAdmin):
    list_filter = ('diff_num', 'style', 'track__pack')


class TrackAdmin(ModelAdmin):
    list_filter = ('pack',)


class Track(models.Model):

    def __str__(self):
        return '%s (%s)' % (self.name, self.pack)

    name = models.CharField(max_length=100)
    min_bpm = models.IntegerField()
    max_bpm = models.IntegerField()
    pack = models.CharField(max_length=100)
    author = models.CharField(max_length=100)


class Stepchart(models.Model):

    def __str__(self):
        return '%s (%s %s)' % (self.track.name, self.style, self.diff_num)

    diff_num = models.IntegerField()
    diff_text = models.CharField(choices=LEVELS, max_length=20)
    comment = models.TextField(null=True)
    track = models.ForeignKey('Track')
    style = models.CharField(choices=STYLES, max_length=20)


class Tracklist(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=100)
    description = models.TextField()
    stepcharts = models.ManyToManyField('Stepchart')


class Tag(models.Model):
    def __str__(self):
        return self.tag
    tag = models.CharField(max_length=20)
    stepcharts = models.ManyToManyField('Stepchart')


class Result(models.Model):

    # todo meta ordering by date descending
    def __str__(self):
        return '%s: %.2f' % (self.stepchart.__str__(), self.percentage)
    percentage = models.FloatField()
    date = models.DateField(auto_now_add=True)
    comment = models.TextField(null=True)
    modifiers = models.ForeignKey('Mods')
    stepchart = models.ForeignKey('Stepchart')


class Mods(models.Model):
    speed = models.FloatField()
    mini = models.IntegerField()
    rate = models.FloatField(default=1)
    others = models.TextField(null=True)