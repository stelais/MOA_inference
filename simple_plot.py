import pandas as pd
from bokeh.models import Whisker, ColumnDataSource, Span, BoxAnnotation
from bokeh.plotting import figure, show


def data_collector(data_file_path, type_file):
    if type_file == 'CFHT':
        column_names = ["HJD", "i-mag", "merr", "airmass", "seeing"]
        df = pd.read_csv(data_file_path, comment='#', header=None, delim_whitespace=True,
                         names=column_names)
        times = df['HJD'] - 2450000.0
        magnitudes = df['i-mag']
        magnitudes_err = df['merr']
        return times, magnitudes, magnitudes_err
    elif type_file == 'MOA-V' or type_file == 'MOA-R':
        column_names = ["HJD", "Flux", "Flux_err", "obs_id", "mag", "merr", "fwhm", "background", "photometric_scale"]
        df = pd.read_csv(data_file_path, comment='#', header=None, delim_whitespace=True,
                         names=column_names)
        times = df['HJD'] - 2450000.0
        fluxes = df['Flux']
        fluxes_err = df['Flux_err']
        return times, fluxes, fluxes_err


def plotter(x_axis, y_axis, y_error, p, legend_label='', y_label_name='Magnification', color='purple',
            plot_errorbar=False, t0_error_plot=False, t0=None, t0_error=None):
    """
    Produce plot for the event

    :return: None
    """

    p.xaxis.axis_label = 'Days'
    p.yaxis.axis_label = y_label_name

    p.circle(x_axis, y_axis, fill_alpha=0.2, size=5, legend_label=legend_label, color=color)

    if plot_errorbar:
        upper = [x + e for x, e in zip(y_axis, y_error)]
        lower = [x - e for x, e in zip(y_axis, y_error)]
        source = ColumnDataSource(data=dict(groups=x_axis, counts=y_axis, upper=upper, lower=lower))

        p.add_layout(
            Whisker(source=source, base="groups", upper="upper", lower="lower", level="overlay")
        )

    if t0_error_plot:
        t0_location = Span(location=t0,
                           dimension='height', line_color='red',
                           line_dash='dashed', line_width=1)
        p.add_layout(t0_location)

        box = BoxAnnotation(left=(t0 - t0_error), right=(t0 + t0_error),
                            line_width=1, line_color='black', line_dash='dashed',
                            fill_alpha=0.2, fill_color='orange')

        p.add_layout(box)
    return p


if __name__ == '__main__':
    data_filepath = "/Users/sishitan/Documents/Analysis_MOA2020-135/data/KB200579_i_CFHT.dat"
    times, magnitudes, magnitudes_err = data_collector(data_filepath, 'CFHT')
    p = figure(title="Lightcurve CFHT", plot_width=900, plot_height=300)
    p = plotter(times, magnitudes, magnitudes_err, p, 'CFHT', 'Magnitude')
    show(p)
