import pandas as pd
from bokeh.plotting import figure, output_notebook, show
from bokeh.models import Span, BoxAnnotation
import numpy as np
from astropy.time import Time


def time_converter(t0):
    """
    This function converts t0 from Taka's table to "human-readable" years. This is NOT THE IDEAL conversion.
    :return:
    int(tm.jyear) : Julian Epoch year Human
    """
    t0 = float(t0)
    tm = Time(float(2450000 + t0), format='jd')
    return int(tm.jyear)


def getting_ra_and_dec_perl(field, chip, x, y):
    """
    Use TAKA's perl code to get position in the sky
    """

    import os
    import subprocess
    os.chdir("/Users/sishitan/Documents/MOA/inference_packages/RADEC")

    pipe = subprocess.Popen(["perl", "ccd2sky.pl", field, chip, x, y], stdout=subprocess.PIPE)
    result = str(pipe.stdout.read())

    ra_coor, dec_coor = result.split('RA= ')[-1].split('  Dec= ')
    dec_coor = dec_coor.split("\\n'")[0]

    return ra_coor, dec_coor


def load_microlensing_meta_data_alerts(metadata_alerts_path):
    """
    Loads a microlensing meta data ALERTS file into a Pandas data frame.
    metadata_22862_path = '/Users/sishitan/Documents/MOA/inference_packages/moa9yr_events_oct2018.txt'
    :param metadata_alerts_path:
    :return: The alert meta data frame
    """
    columns_name = ["field","band","chip","subfield","event_id","tag","x","y","tag_0607","sep_0607","ID_0607","x_0607",
              "y_0607","alert_yes","sep_alerts","name_alerts","x_alerts","y_alerts",
                    "alert_yes2","sep_alerts2","name_alerts2","x_alerts2","y_alerts2",
                   "alert_yes3","sep_alerts3","name_alerts3","x_alerts3","y_alerts3"]
    metadata_22862_path_df = pd.read_csv(metadata_alerts_path, comment='#', header=None, delim_whitespace=True,
                                        names=columns_name)
    return metadata_22862_path_df


def load_microlensing_meta_data(meta_data_file_path: str) -> pd.DataFrame:
    """
    Loads a microlensing meta data file into a Pandas data frame.
    '/Users/sishitan/Documents/MOA/inference_packages/candlist_RADec.dat.txt'
    :param meta_data_file_path: The path to the original meta data CSV.
    :return: The meta data frame.
    """

    column_names = ['field', 'chip', 'nsub', 'ID', 'RA', 'Dec', 'x', 'y', 'ndata', 'ndetect', 'sigma', 'sumsigma',
                    'redchi2_out', 'sepmin', 'ID_dophot', 'type', 'mag', 'mage', 't0', 'tE', 'umin', 'fs', 'fb',
                    't0e', 'tEe', 'tEe1', 'tEe2', 'umine', 'umine1', 'umine2', 'fse', 'fbe', 'chi2', 't0FS', 'tEFS',
                    'uminFS', 'rhoFS', 'fsFS', 'fbFS', 't0eFS', 'tEeFS', 'tEe1FS', 'tEe2FS', 'umineFS', 'umine1FS',
                    'umine2FS', 'rhoeFS', 'rhoe1FS', 'rhoe2FS', 'fseFS', 'fbeFS', 'chi2FS']
    meta_dataframe = pd.read_csv(meta_data_file_path, comment='#', header=None, delim_whitespace=True,
                                 names=column_names)
    return meta_dataframe


class Event:
    """
    Event
    """

    def __init__(self, field=None, band=None, chip=None, subfield=None, event_id=None,
                 event_name=None, t0=None, t0_error=None):
        self.field = field
        self.band = band
        self.chip = chip
        self.subfield = subfield
        self.event_id = event_id
        self.event_name = event_name
        self.t0 = t0
        self.t0_error = t0_error

    def use_name_to_define(self):
        no_suffix = self.event_name.split(".")[0]
        field_, band_, chip_, subfield_, event_id_ = no_suffix.split("-")
        self.field = field_
        self.band = band_
        self.chip = chip_
        self.subfield = subfield_
        self.event_id = event_id_
        return field_, band_, chip_, subfield_, event_id_

    def getting_t0_from_metadata(self, meta_dataframe):
        lightcurve_meta_data = meta_dataframe[(meta_dataframe['ID'] == int(self.event_id)) &
                                              (meta_dataframe['field'] == self.field) &
                                              (meta_dataframe['chip'] == int(self.chip)) &
                                              (meta_dataframe['nsub'] == int(self.subfield))]

        self.t0 = lightcurve_meta_data["t0"]
        self.t0_error = lightcurve_meta_data["t0e"]
        return self.t0, self.t0_error

    def getting_RADec_from_metadata(self, meta_dataframe):
        """
        Return sky coordinates from the candRADec metadata frame
        :param meta_dataframe:
        :return:  ra_coordinate, dec_coordinate
        """
        lightcurve_meta_data = meta_dataframe[(meta_dataframe['ID'] == int(self.event_id)) &
                                              (meta_dataframe['field'] == self.field) &
                                              (meta_dataframe['chip'] == int(self.chip)) &
                                              (meta_dataframe['nsub'] == int(self.subfield))]

        ra_coordinate = lightcurve_meta_data["RA"]
        dec_coordinate = lightcurve_meta_data["Dec"]
        return ra_coordinate, dec_coordinate

    def getting_XY_from_metadata(self, meta_dataframe):
        """
        Return pixels from the candRADec metadata frame
        :param meta_dataframe:
        :return:  x_coordinate, y_coordinate
        """
        lightcurve_meta_data = meta_dataframe[(meta_dataframe['ID'] == int(self.event_id)) &
                                              (meta_dataframe['field'] == self.field) &
                                              (meta_dataframe['chip'] == int(self.chip)) &
                                              (meta_dataframe['nsub'] == int(self.subfield))]

        x_coordinate = lightcurve_meta_data["x"]
        y_coordinate = lightcurve_meta_data["y"]
        return x_coordinate, y_coordinate

    def producing_plots(self, data_directory):
        """
        Produce plot for the event
        :param data_directory: where times and fluxes are
        :return: None
        """
        print(self.event_name)
        # df = pd.read_csv(filename)
        # times = df['HJD']
        # fluxs = df['flux']
        # flux_errs = df['flux_err']
        t0 = float(self.t0)
        t0_error = float(self.t0_error)
        data = np.loadtxt(data_directory + self.event_name)
        times = data[:, 0]
        fluxes = data[:, 1]
        fluxes_error = data[:, 2]
        p = figure(title="Lightcurve " + str(self.event_name), plot_width=900, plot_height=300)
        p.xaxis.axis_label = 'Days'
        p.yaxis.axis_label = 'Flux'

        t0_location = Span(location=t0,
                           dimension='height', line_color='red',
                           line_dash='dashed', line_width=1)
        p.add_layout(t0_location)

        box = BoxAnnotation(left=(t0 - t0_error), right=(t0 + t0_error),
                            line_width=1, line_color='black', line_dash='dashed',
                            fill_alpha=0.2, fill_color='orange')

        p.add_layout(box)
        p.circle(times, fluxes, fill_alpha=0.2, size=5)
        show(p)


if __name__ == '__main__':
    metadata_path = '/Users/sishitan/Documents/MOA/inference_packages/candlist_RADec.dat.txt'
    meta_dataframe = load_microlensing_meta_data(metadata_path)
    metadata_22862_path = '/Users/sishitan/Documents/MOA/inference_packages/moa9yr_events_oct2018.txt'
    data_directory = '/Users/sishitan/Documents/MOA/inference_Jul_Aug/MOA_microlensing_4/Inference_on_positives/'
    filename = 'gb9-R-4-5-234724.phot.cor'
    event = Event(event_name=filename)
    field, band, chip, subfield, event_id = event.use_name_to_define()
    event.getting_t0_from_metadata(meta_dataframe)
    t0_human = time_converter(event.t0)
    print(f"t0: {float(event.t0)} +/- {float(event.t0_error)} days, which is in year {t0_human}")
    ra_coor, dec_coor = event.getting_RADec_from_metadata(meta_dataframe)
    print("ra_coor: ", ra_coor, "\ndec_coor: ", dec_coor)
    x_coor, y_coor = event.getting_XY_from_metadata(meta_dataframe)
    print("x_coor: ", x_coor, "\ny_coor: ", y_coor)
    event.producing_plots(data_directory)
    print(getting_ra_and_dec_perl(str(field[-1]), str(chip), str(float(x_coor)), str(float(y_coor))))
