# coding: utf-8
from pathlib import Path


class MicapsType4Data(object):
    def __init__(self):
        self.data_type = 4
        self.comment = None
        self.start_time = None
        self.forecast_hour = None
        self.level = None
        self.x_step = None
        self.y_step = None
        self.x_start_value = None
        self.x_end_value = None
        self.y_start_value = None
        self.y_end_value = None
        self.x_count = None
        self.y_count = None
        self.contour_step = 4.00
        self.contour_start_value = None
        self.contour_end_value = None
        self.smooth = 2
        self.bold_value = 0.00
        self.values = None


class MicapsType4Writer(object):
    def __init__(self):
        pass

    @classmethod
    def write_to_file(cls, micaps_data, output_file_path):
        output_dir_path = Path(output_file_path).parent
        output_dir_path.mkdir(parents=True, exist_ok=True)
        with open(str(output_file_path), 'w') as output_file:
            output_file.write("diamond ")
            output_file.write("{data_type} {comment}\n".format(
                data_type=micaps_data.data_type,
                comment=micaps_data.comment
            ))

            output_file.write("{year:02d} {month:02d} {day:02d} {hour:02d} {forecast_hour:03d} {level}\n".format(
                year=micaps_data.start_time.year % 100,
                month=micaps_data.start_time.month,
                day=micaps_data.start_time.day,
                hour=micaps_data.start_time.hour,
                forecast_hour=micaps_data.forecast_hour,
                level=int(micaps_data.level)
            ))

            output_file.write(
                "{x_step:.2f} {y_step:.2f} {x_start_value:.2f} {x_end_value:.2f} {y_start_value:.2f} {y_end_value:.2f} "
                "{x_count} {y_count} {contour_step:.2f} {contour_start_value:.2f} {contour_end_value:.2f} "
                "{smooth:.2f} {bold_value:.2f}\n".format(
                    x_step=micaps_data.x_step,
                    y_step=micaps_data.y_step,
                    x_start_value=micaps_data.x_start_value,
                    x_end_value=micaps_data.x_end_value,
                    y_start_value=micaps_data.y_start_value,
                    y_end_value=micaps_data.y_end_value,
                    x_count=micaps_data.x_count,
                    y_count=micaps_data.y_count,
                    contour_step=micaps_data.contour_step,
                    contour_start_value=micaps_data.contour_start_value,
                    contour_end_value=micaps_data.contour_end_value,
                    smooth=micaps_data.smooth,
                    bold_value=micaps_data.bold_value
                ))

            index = 0
            for i in micaps_data.values:
                output_file.write("  {value:.2f}".format(value=i))
                if (index + 1) % 10 == 0 or (index + 1) % micaps_data.y_count == 0:
                    output_file.write("\n")
                index += 1
