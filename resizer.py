import os
from PIL import Image, UnidentifiedImageError
from shutil import copyfile
import configparser
from openpyxl import Workbook
from datetime import datetime


# pyinstaller --onefile resizer.py --distpath resizer

class ImagesFolder:
    convert_filenames_to_url = False
    rename_files_as_dir = False
    regenerate_files = True
    resize_size = (1200, 1200)
    print_current_file = True

    resize_images = False
    center_when_upscaling = True

    tmb_flag = False
    tmb_size = (300, 300)

    script_root_path = os.getcwd()
    src_root_path = os.path.join(script_root_path, 'input_dir')
    dst_root_path = os.path.join(script_root_path, 'output_dir')

    link_path = ''

    def __init__(self, folder_path, files_inside):

        self.src_folder_name = os.path.relpath(folder_path, inputpath)
        self.src_folder_name_url_converted = convert_to_url(self.src_folder_name)
        self.dst_folder_name = \
            self.src_folder_name_url_converted if self.convert_filenames_to_url else self.src_folder_name

        self.src_folder_path = folder_path
        self.dst_folder_path = os.path.join(self.dst_root_path, self.dst_folder_name)

        self.src_photo_names_arr = [file for file in files_inside if file.lower().endswith('.jpg')]
        self.src_photo_paths_arr = [os.path.join(self.src_folder_path, file) for file in self.src_photo_names_arr]

        self.dst_photo_names_arr = []
        self.fill_dst_photo_names()

        self.dst_photo_paths_arr = \
            [os.path.join(self.dst_folder_path, filename) for filename in self.dst_photo_names_arr]
        self.dst_photo_links_arr = \
            [self.link_path + self.dst_folder_name + "/" + file for file in self.dst_photo_names_arr]

        self.errors_arr = []

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def generate_output_folder(self):
        if not os.path.isdir(self.dst_folder_path):
            os.mkdir(self.dst_folder_path)
            print('Processing ' + self.dst_folder_path)
            return True
        elif self.regenerate_files:
            for item in os.listdir(self.dst_folder_path):
                os.remove(os.path.join(self.dst_folder_path, item))
            return True
        else:
            print(self.src_folder_path + " Output folder already exits!")
            return False

    def fill_dst_photo_names(self):
        dst_photo_names_arr = []
        for photo_number in range(len(self.src_photo_names_arr)):
            if self.rename_files_as_dir:
                new_filename = self.src_folder_name + "_" + str(photo_number).zfill(3) + ".jpg"
            else:
                new_filename = self.src_photo_names_arr[photo_number]
            if self.convert_filenames_to_url:
                new_filename = convert_to_url(new_filename)

            dst_photo_names_arr.append(new_filename)
        self.dst_photo_names_arr = dst_photo_names_arr

    def generate_output_files(self):
        for photo_number in range(len(self.src_photo_names_arr)):
            if self.resize_images:
                if not resize_tmb_img(
                        self.src_photo_paths_arr[photo_number],
                        self.dst_photo_paths_arr[photo_number],
                        self.resize_size,
                        center=self.center_when_upscaling):
                    self.errors_arr.append(self.src_photo_paths_arr[photo_number])
            else:
                copyfile(self.src_photo_paths_arr[photo_number], self.dst_photo_paths_arr[photo_number])

            if self.print_current_file:
                print('File', self.src_photo_paths_arr[photo_number], 'processed.')
        if self.tmb_flag:
            self.generate_tmb()

    def generate_tmb(self):
        if self.src_photo_paths_arr[0]:
            if self.rename_files_as_dir:
                tmb_dst_filename = self.dst_folder_name + '_tmb.jpg'
            else:
                tmb_dst_filename = os.path.splitext(self.dst_photo_names_arr[0])[0]
                tmb_dst_filename = tmb_dst_filename + '_tmb.jpg'

            dst_tmb_filepath = os.path.join(self.dst_folder_path, tmb_dst_filename)

            if not resize_tmb_img(
                    self.src_photo_paths_arr[0],
                    dst_tmb_filepath,
                    self.tmb_size,
                    center=self.center_when_upscaling):
                self.errors_arr.append('Error while generating tmb from ' + str(self.src_photo_paths_arr[0]))
            else:
                self.dst_photo_names_arr.append(tmb_dst_filename)
                self.src_photo_paths_arr.append(dst_tmb_filepath)
                if self.print_current_file:
                    print('Tmb for', self.src_photo_paths_arr[0], 'created.')
        else:
            self.errors_arr.append('No src file for tmb in ' + str(self.src_folder_path))

    def get_process_report_by_dir(self):
        return [self.src_folder_name, self.dst_folder_name, *self.dst_photo_links_arr]

    def get_process_report_by_file(self):
        files_arr = []
        for i in range(len(self.src_photo_names_arr)):
            files_arr.append([
                self.src_photo_names_arr[i],
                self.dst_photo_names_arr[i],
                self.dst_photo_links_arr[i]
                 ])
        return files_arr


def gen_config():
    with open('resizer_config.ini', 'w+') as f:
        conf_str = ('[global_settings]\n'
                    'rename_flag = True\n'
                    'url_flag = False\n'
                    'url_replace = +, ,/,%%\n'
                    'regenerate = True\n'
                    'list_files_flag = False\n'
                    '# set True to activate file-based output (old-filename, new-filename, path)\n'
                    '# when True deactivates tmb flag\n'
                    'separate_files = True\n'
                    '\n'
                    '[img_settings]\n'
                    'resize_flag = True\n'
                    'center_flag = True\n'
                    'resize_width = 1200\n'
                    'resize_height = 1200\n'
                    'tmb_flag = True\n'
                    'tmb_size = 300\n'
                    '\n'
                    '[paths]\n'
                    'site_path = loft-it.ru/docs/_shop/loft_it/\n'
                    'paths_output_file_format = resizer_output_%%d-%%m-%%Y_%%H-%%M-%%S')
        f.write(conf_str)


def convert_to_url(text):
    text = text.lower()
    for symbol in url_replace:
        text = text.replace(symbol, "-")
    return text


def resize_tmb_img(img_src_path, img_dst_path, out_size, center=True):
    try:
        im = Image.open(img_src_path).convert('RGB')
    except UnidentifiedImageError:
        print('Format of', img_src_path, 'is not jpg!')
        return False
    except:
        print('Something wrong with', img_src_path)
        return False

    im.thumbnail(out_size)
    img_size = im.size

    new_im = Image.new('RGB', out_size, im.getpixel((1, 1)))
    # new_im = Image.new('RGB', out_size)

    vert_margin = round((out_size[1] - img_size[1]) / 2)
    hor_margin = round((out_size[0] - img_size[0]) / 2)
    if center:
        margins = (hor_margin, vert_margin)
    elif img_size[0] > img_size[1]:
        margins = (0, vert_margin)
    else:
        margins = (hor_margin, 0)

    new_im.paste(im, box=margins)
    # new_im.show()
    new_im.save(img_dst_path, "JPEG", subsampling=0)

    return True


def do_the_job():
    errors_arr = []

    wb = Workbook()
    ws = wb.active
    ws.append(['src folder', 'dst folder', 'photos'])

    for current_dir_path, subdir_names, files_inside in os.walk(inputpath):

        if current_dir_path == inputpath:
            # nothing to do in root
            continue
            # print("root")
        elif "\\" in os.path.relpath(current_dir_path, inputpath):
            # if subdir
            print("skipping subdir " + str(os.path.relpath(current_dir_path, inputpath)))
            continue

        # if not subdir
        this_dir_obj = ImagesFolder(current_dir_path, files_inside)
        if not this_dir_obj.generate_output_folder():
            continue
        this_dir_obj.generate_output_files()

        if separate_files:
            for file in this_dir_obj.get_process_report_by_file():
                ws.append(file)
        else:
            ws.append(this_dir_obj.get_process_report_by_dir())

        errors_arr = [*errors_arr, *this_dir_obj.errors_arr]

    datetime_now = datetime.now()
    paths_output_file = datetime_now.strftime(paths_output_file_format) + '.xlsx'
    wb.save(paths_output_file)

    if errors_arr:
        print('These files were not processed due to resize error:')
        print(errors_arr)


if __name__ == '__main__':

    filenames_arr = []
    inputpath = os.path.join(os.getcwd(), "original_img")
    outputpath = os.path.join(os.getcwd(), "output_img")

    ImagesFolder.src_root_path = inputpath
    ImagesFolder.dst_root_path = outputpath

    if not os.path.isdir(inputpath):
        os.mkdir(inputpath)
    if not os.path.isdir(outputpath):
        os.mkdir(outputpath)
    if not os.path.isfile('resizer_config.ini'):
        gen_config()

    config = configparser.ConfigParser()  # создаём объекта парсера
    config.read("resizer_config.ini")  # читаем конфиг

    ImagesFolder.rename_files_as_dir = config["global_settings"].getboolean("rename_flag")

    ImagesFolder.convert_filenames_to_url = config["global_settings"].getboolean("url_flag")
    url_replace = config["global_settings"]["url_replace"]
    url_replace = url_replace.split(",")
    ImagesFolder.regenerate_files = config["global_settings"].getboolean("regenerate")
    ImagesFolder.print_current_file = config["global_settings"].getboolean("list_files_flag")
    separate_files = config["global_settings"].getboolean("separate_files")

    ImagesFolder.resize_images = config["img_settings"].getboolean("resize_flag")
    ImagesFolder.center_when_upscaling = config["img_settings"].getboolean("center_flag")
    resize_width = config["img_settings"].getint("resize_width")
    resize_height = config["img_settings"].getint("resize_height")
    ImagesFolder.resize_size = (resize_width, resize_height)

    ImagesFolder.tmb_flag = config["img_settings"].getboolean("tmb_flag")
    tmb_size = config["img_settings"].getint("tmb_size")
    ImagesFolder.tmb_size = (tmb_size, tmb_size)

    ImagesFolder.link_path = config["paths"]["site_path"]
    paths_output_file_format = config["paths"]["paths_output_file_format"]

    if separate_files:
        ImagesFolder.tmb_flag = False

    do_the_job()

    print('DONE!')
    input('Press Enter to exit...')
