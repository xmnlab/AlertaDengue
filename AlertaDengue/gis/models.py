from django.db import models
from django.utils.translation import ugettext_lazy as _


class SatelliteClimate(models.Model):
    """
    geocode INT NOT NULL,
    forecast_model_id INT,
    active BOOL NOT NULL,

    """
    city = models.ForeignKey(
        'dados.City', db_column='geocode', null=False,
        help_text=_('Código do Município'), on_delete=models.DO_NOTHING
    )
    images_date = models.DateField(
        db_column='images_date', null=False, help_text=_('Data das imagens')
    )
    ndvi = models.FloatField(
        db_column='ndvi', null=False, help_text=_('Valor médio NDVI')
    )
    temperature_max = models.FloatField(
        db_column='temperature_max',
        help_text='Valor médio de Temperatura Máxima'
    )
    temperature_min = models.FloatField(
        db_column='temperature_min',
        help_text='Valor médio Temperatura Mínima'
    )
    precipitation = models.FloatField(
        db_column='precipitation',
        help_text='Valor médio de Precipitação'
    )
    relative_humidity = models.FloatField(
        db_column='relative_humidity',
        help_text='Valor médio de Umidade Relativa'
    )
    specific_humidity = models.FloatField(
        db_column='specific_humidity',
        help_text='Valor médio de Umidade Específica'
    )

    class Meta:
        db_table = 'Municipio\".\"clima_satelite'
        app_label = 'gis'
        verbose_name_plural = "satellite_climates"
        unique_together = (('city', 'images_date'),)
        managed = False

    def __str__(self):
        return '%s - %s' % (self.city, self.images_date)
