import os
import PIL
from PIL import Image
from shutil import copyfile
import configparser


# pyinstaller --onefile resizer.py --distpath resizer


def gen_config():
    with open('resizer_config.ini', 'w+') as f:
        conf_str = ('[global_settings]\n'
                    'rename_flag = True\n'
                    'url_flag = False\n'
                    'url_replace = +, ,/,%%\n'
                    'regenerate = True\n'
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
                    'site_path = loft-it.ru/docs/_shop/loft_it/')
        f.write(conf_str)


def prepare_for_url(text):
    text = text.lower()
    for symbol in url_replace:
        text = text.replace(symbol, "-")
    return text


def resize_tmb_img(img_name, img_src_path, img_dst_path, img_dst_name, out_size, center=True):
    try:
        im = Image.open(os.path.join(img_src_path, img_name)).convert('RGB')
    except PIL.UnidentifiedImageError:
        print('Format of', img_name, 'at', img_src_path, 'is not jpg!')
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
    # new_im.save(os.path.join(img_dst_path, img_dst_name), "JPEG")
    new_im.save(os.path.join(img_dst_path, img_dst_name), "JPEG", subsampling=0)

    return True


def do_the_job():
    errors_arr = []
    for dirpath, dirnames, filenames in os.walk(inputpath):

        if dirpath == inputpath:
            # nothing to do in root
            continue
            # print("root")
        elif "\\" in os.path.relpath(dirpath, inputpath):
            # if subdir
            print("skipping subdir " + str(os.path.relpath(dirpath, inputpath)))
            continue

        # if not subdir
        if url_flag:
            artikul = prepare_for_url(os.path.relpath(dirpath, inputpath))
        else:
            artikul = os.path.relpath(dirpath, inputpath)

        out_path = os.path.join(outputpath, artikul)

        if not os.path.isdir(out_path):
            os.mkdir(out_path)
            print('Processing ' + dirpath)
        elif regenerate:
            for item in os.listdir(out_path):
                os.remove(os.path.join(out_path, item))
        else:
            print(dirpath + " Folder does already exits!")
            continue

        # remove everything except jpg
        for file in filenames[::-1]:
            if not file.lower().endswith('.jpg'):
                filenames.remove(file)

        # generate thumbnails
        if tmb_flag:
            if not resize_tmb_img(filenames[0], dirpath, out_path, artikul + "_tmb" + ".jpg", tmb_size):
                errors_arr.append((dirpath, filenames[0]))
                continue
        # print("artikul: " + os.path.relpath(dirpath, inputpath))

        counter = 0
        out_filenames = []
        for file in filenames:
            # print('in dir ' + os.path.relpath(dirpath, inputpath) + " there are file " + file)

            counter += 1

            if rename_flag:
                out_filename = artikul + "_" + str(counter).zfill(3) + ".jpg"
            else:
                out_filename = file

            if url_flag:
                out_filename = prepare_for_url(out_filename)

            out_filenames.append([out_filename, artikul])
            if resize_flag:
                if not resize_tmb_img(file, dirpath, out_path, out_filename, resize_size, center=center_flag):
                    errors_arr.append((dirpath, file))
                    continue
            else:
                # print("copying" + os.path.join(dirpath, file) + " to " + os.path.join(out_path, out_filename))
                copyfile(os.path.join(dirpath, file), os.path.join(out_path, out_filename))
        filenames_arr.append(out_filenames)
    if errors_arr:
        print('These files were not processed due to resize error:')
        print(errors_arr)

    if url_flag:
        with open("filenames.txt", 'w') as f:
            for art in filenames_arr:
                out_str = ""
                for file in art:
                    out_str += remote_filepath + file[1] + "/" + file[0] + ";"
                f.write(out_str + "\n")
    else:
        if os.path.exists("filenames.txt"):
            os.remove("filenames.txt")


if __name__ == '__main__':

    filenames_arr = []
    inputpath = os.path.join(os.getcwd(), "original_img")
    outputpath = os.path.join(os.getcwd(), "output_img")

    if not os.path.isdir(inputpath):
        os.mkdir(inputpath)
    if not os.path.isdir(outputpath):
        os.mkdir(outputpath)
    if not os.path.isfile('resizer_config.ini'):
        gen_config()

    config = configparser.ConfigParser()  # создаём объекта парсера
    config.read("resizer_config.ini")  # читаем конфиг

    rename_flag = config["global_settings"].getboolean("rename_flag")

    url_flag = config["global_settings"].getboolean("url_flag")
    url_replace = config["global_settings"]["url_replace"]
    url_replace = url_replace.split(",")
    regenerate = config["global_settings"].getboolean("regenerate")

    resize_flag = config["img_settings"].getboolean("resize_flag")
    center_flag = config["img_settings"].getboolean("center_flag")
    resize_width = config["img_settings"].getint("resize_width")
    resize_height = config["img_settings"].getint("resize_height")
    resize_size = (resize_width, resize_height)

    tmb_flag = config["img_settings"].getboolean("tmb_flag")
    tmb_size = config["img_settings"].getint("tmb_size")
    tmb_size = (tmb_size, tmb_size)

    remote_filepath = config["paths"]["site_path"]

    do_the_job()

    print('DONE!')
    input('Press Enter to exit...')
