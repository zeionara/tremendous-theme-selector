import os
import random
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread

import click
import pygame

from tremendous_theme_selector.utils import get_all_files, get_binary_label, stringify_annotations, write_lines, parse_annotations, play_file


@click.group()
def main():
    pass


@main.command()
@click.argument('input-folder-path', type=str)
@click.option('-i', '--input-labels-file-path', default=None, type=str)
# @click.option('-o', '--output-labels-file-path', default='assets/output-labels.txt', type=str)
@click.option('-n', '--n-files-to-annotate', default=None, type=int)
@click.argument('output-labels-file-paths', type=str, nargs=-1)
def annotate_with_binary_labels(input_folder_path, input_labels_file_path, output_labels_file_paths, n_files_to_annotate):
    assert input_labels_file_path not in output_labels_file_paths
    pygame.mixer.init()
    files = list(get_all_files(input_folder_path))
    if input_labels_file_path is not None:
        parsed_labels = parse_annotations(input_labels_file_path)
        files = [
            file
            for file in files
            if file not in parsed_labels
        ]
    annotations = {
        output_labels_file_path: {}
        for output_labels_file_path in output_labels_file_paths
    }
    counter = 0
    flags = [True, ]
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            while len(files) > 0:
                chosen_file = random.choice(files)
                print(f'Annotating file {chosen_file}' + (f' {counter + 1}/{n_files_to_annotate}' if n_files_to_annotate is not None else ''))
                score_future = executor.submit(get_binary_label, output_labels_file_paths)
                play_thread = Thread(target=play_file, args=(chosen_file, flags))
                play_thread.start()
                for output_labels_file_path, label in score_future.result().items():
                    annotations[output_labels_file_path][chosen_file] = label
                flags[0] = False
                counter += 1
                files.remove(chosen_file)
                if n_files_to_annotate is not None and counter >= n_files_to_annotate:
                    print(f'Good job! You have annotated {n_files_to_annotate} files!')
                    break
            else:
                print('Good job! You have annotated all the files!')
    # except:
    #     print(f'Good job! You have annotated {counter} files!')
    finally:
        for output_labels_file_path in annotations:
            os.makedirs(os.path.dirname(os.path.realpath(output_labels_file_path)), exist_ok=True)
            write_lines(
                output_labels_file_path,
                stringify_annotations(annotations[output_labels_file_path])
            )


if __name__ == '__main__':
    main()
