#!/usr/bin/env python3

# Import required modules
from __future__ import unicode_literals

import tempfile
from atexit import register
from datetime import datetime
from os import environ, makedirs, path, remove, walk
from pathlib import Path as FilePath
from shutil import make_archive, move as move_file
from subprocess import call, check_output  # noqa: S404
from sys import argv, exit
from typing import List

import easyparse

from flask import Flask, render_template, request, safe_join, send_from_directory

from gevent.pywsgi import WSGIServer

import youtube_dl

from .install_packages import OSInteractionLayer

VERSION_STRING = " * HomePage, v0.3.0\n * Copyright (c) 2019 Sh3llcod3. (MIT License)"
WSGI_PORT = environ.get("HOMEPAGE_PORT", 5000)
REQUEST_LOGLEVEL = environ.get("HOMEPAGE_REQUEST_LOG", None)
LOG_DOWNLOAD = environ.get("HOMEPAGE_DOWNLOAD_LOG", 1)

# Get the environment paths
STORAGE_FOLDER = FilePath(environ.get("HOMEPAGE_STORAGE", path.expanduser("~/.homepage_storage")))


# Setup our youtube_dl logger class.
class YTDLLogger():
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def ytdl_hook(progress):
    if progress['status'] == 'finished':
        if bool(LOG_DOWNLOAD):
            print(' * Downloaded video, now converting...')


# Setup our Video class, this will handle the youtube_dl side of things.
class Video():

    # Initialise the class.
    def __init__(self, post_request, temp_download_dir):
        self.post_request = post_request
        self.temp_download_dir = temp_download_dir
        self.video_link = post_request["videoURL"]
        self.mime_type = post_request["format_preference"]
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': f'{self.mime_type}',
                    'preferredquality': post_request["quality_preference"],
                },
                {
                    'key': 'FFmpegMetadata',
                }
            ],
            'logger': YTDLLogger(),
            'progress_hooks': [ytdl_hook],
            'outtmpl': f'{temp_download_dir}/%(title)s.%(ext)s'
        }
        if post_request["attach_thumb"].lower() == "yes":
            self.ydl_opts["writethumbnail"] = True
            self.ydl_opts["postprocessors"].append({'key': 'EmbedThumbnail', })
        if self.mime_type == "m4a":
            self.ydl_opts['postprocessor_args'] = [
                '-strict', '-2'
            ]

    # Add our download() method to download the video.
    def download(self):
        with youtube_dl.YoutubeDL(self.ydl_opts) as self.ydl:
            self.ydl.download([self.video_link])

    # Add our send_files() method to handle transfer.
    def send_files(self):
        path, dirs, files = next(walk(self.temp_download_dir))
        file_count = len(files)
        self.final_file_name = str()

        # The link is invalid
        if file_count == 0:
            return render_template("error_template.html")

        # We have more than one file, so let's zip them up and send them back.
        if file_count > 1:
            self.final_file_name = "tracks_" + str(datetime.now().timestamp()).replace('.', '')
            self.final_file_location = FilePath("/tmp/")  # noqa: S108
            make_archive(self.final_file_location / self.final_file_name, 'zip', self.temp_download_dir)
            self.final_file_location /= (self.final_file_name + ".zip")
            self.mime_type = "application/zip"
            move_file(str(self.final_file_location), STORAGE_FOLDER)
            self.final_file_name += ".zip"

        # We only have one track, so let's send the file back.
        else:
            self.final_file_name = next(walk(self.temp_download_dir))[2][0]
            move_file(safe_join(self.temp_download_dir, self.final_file_name), STORAGE_FOLDER)

        return safe_join("./transfer/", self.final_file_name)


list_item_template = """<li class="mdc-list-item">
    <span class="mdc-list-item__text">{file_full_name}</span>
    <span class="mdc-list-item__meta material-icons" aria-hidden="true" title="Download Track" onclick="getPreviousTrack('{previous_trackpath}')">cloud_download</span>
</li>"""  # noqa: E501


# Generate the html elements for the previous files.
def update_file_list():
    path, dirs, files = next(walk(STORAGE_FOLDER))
    prev_count = len(files)
    if prev_count == 0:
        return ["", ""]
    elif prev_count > 0:
        list_buffer = str()
        end_js = 'document.getElementById("Previous-Track-Table").style.display = "block";'
        for i in files:
            list_buffer += list_item_template.format(file_full_name=i, previous_trackpath=safe_join("./transfer/", i))
        return [list_buffer, end_js]


app = Flask(__name__, static_url_path='/static')


@app.route('/', methods=["GET", "POST"])
def index_page():
    if request.method == "GET":
        table_items, js_addition = update_file_list()
        return render_template("./site.html", previous_items=table_items, extra_js=js_addition)

    if request.method == "POST":
        with tempfile.TemporaryDirectory() as temp_dirpath:
            dl_request = Video(request.form, temp_download_dir=temp_dirpath)
            dl_request.download()
            return dl_request.send_files()


@app.route('/transfer/<filepath>', methods=["GET"])
def download_file(filepath):
    return send_from_directory(STORAGE_FOLDER, filepath, as_attachment=True)


@app.route('/update_state', methods=["GET"])
def update_file_state():
    return update_file_list()[0]


def main():

    # Setup our required packages
    pkg_mgr = OSInteractionLayer()

    # Setup our argument parser
    if pkg_mgr.IS_WINDOWS:
        parser = easyparse.opt_parser(argv, show_colors=False)
    else:
        parser = easyparse.opt_parser(argv)

    parser.add_comment("Deploy for the first time: homepage -fdip")
    parser.add_comment("Deploy the app normally: homepage -df")
    parser.add_comment("This app isn't designed to scale at all, on purpose.")
    parser.add_comment("Please don't deploy this outside your internal network.")
    parser.add_arg(
        "-h",
        "--help",
        None,
        "Show this help screen and exit.",
        optional=True
    )
    parser.add_arg(
        "-v",
        "--version",
        None,
        "Print version information and exit.",
        optional=True
    )
    parser.add_arg(
        "-d",
        "--deploy-app",
        None,
        "Deploy the app and start the WSGI server.",
        optional=False
    )
    parser.add_arg(
        "-f",
        "--forward-to-all-hosts",
        None,
        "Add an iptables rule forwarding port 80 to WSGI server port for convenience.",
        optional=False
    )
    parser.add_arg(
        "-p",
        "--purge-cache",
        None,
        "If supplied, remove all past downloaded tracks.",
        optional=False
    )
    parser.add_arg(
        "-i",
        "--install-dependencies",
        None,
        "Install some apt dependencies, only need to run once.",
        optional=False
    )
    parser.add_arg(
        "-c",
        "--compile-ffmpeg",
        None,
        "Treat node as tty only, compile latest FFMPEG from GitHub.",
        optional=True
    )
    parser.parse_args()

    # View the help screen
    if parser.is_present("-h") or len(argv) == 1:
        parser.filename = "homepage"
        parser.show_help()
        exit()

    # Print the version.
    if parser.is_present("-v"):
        print(VERSION_STRING)
        exit()

    # Add the iptables rule
    if not pkg_mgr.IS_WINDOWS:
        active_interface = check_output("route | grep '^default' | grep -o '[^ ]*$'",  # noqa: S607
                                         shell=True).decode('utf-8').rstrip()  # noqa: S602

    def remove_rule():
        print("\n * Reverting iptables rule.")
        call((f"sudo iptables -t nat -D PREROUTING -i {active_interface} "  # noqa: S607
              f"-p tcp --dport 80 -j REDIRECT --to-port {WSGI_PORT}"), shell=True)  # noqa: S602

    if parser.is_present("-f"):
        if not pkg_mgr.IS_WINDOWS:
            print(" * Adding iptables rule.")
            call((f"sudo iptables -t nat -A PREROUTING -i {active_interface} "  # noqa: S607
                  f"-p tcp --dport 80 -j REDIRECT --to-port {WSGI_PORT}"), shell=True)  # noqa: S602
            register(remove_rule)
        else:
            print(" * Skipping iptables rule since host is Windows.")

    # Delete the previous downloaded tracks
    if parser.is_present("-p"):
        print(" * Purging downloaded tracks.")
        try:
            for cached_item in next(walk(STORAGE_FOLDER))[2]:
                remove(STORAGE_FOLDER / cached_item)
        except(StopIteration):
            pass

    # Treat as tty only, don't pull in x-org deps.
    if parser.is_present("-c"):
        ffmpeg_install_dir = FilePath(path.expanduser('~/.ffmpeg'))

        deb_pkg_build: List[str] = [
            "apt",
            "sudo apt update",
            ("sudo apt -y install autoconf "
             "automake "
             "build-essential "
             "cmake "
             "git-core "
             "libass-dev "
             "libfreetype6-dev "
             "libtool "
             "libvorbis-dev "
             "pkg-config "
             "texinfo "
             "wget "
             "zlib1g-dev "
             "nasm "
             "yasm "
             "libx264-dev "
             "libx265-dev "
             "libnuma-dev "
             "libvpx-dev "
             "libfdk-aac-dev "
             "libmp3lame-dev "
             "libopus-dev"),
            f"rm -rf {ffmpeg_install_dir}",
            f"git clone https://github.com/FFmpeg/FFmpeg.git {ffmpeg_install_dir}",
            (f'cd {ffmpeg_install_dir} && git pull --all --prune && ./configure '
             '--pkg-config-flags="--static" '
             '--extra-libs="-lpthread -lm" '
             '--enable-gpl '
             '--enable-libass '
             '--enable-libfdk-aac '
             '--enable-libfreetype '
             '--enable-libmp3lame '
             '--enable-libopus '
             '--enable-libvorbis '
             '--enable-libvpx '
             '--enable-libx264 '
             '--enable-libx265 '
             '--enable-nonfree '
             ' && make -j$(nproc) && '
             ' sudo ln -sf $(readlink -f ffmpeg) /usr/local/bin/ffmpeg && '
             ' sudo ln -sf $(readlink -f ffprobe) /usr/local/bin/ffprobe')
        ]

        pkg_mgr.compile_dist_pkg(
            ubuntu=deb_pkg_build,
            kali=deb_pkg_build,
            mint=deb_pkg_build,
            debian=deb_pkg_build,
            raspbian=deb_pkg_build
        )

    # Install the package dependencies.
    if parser.is_present("-i"):

        # Host is desktop, just install the deps as-is unless specified.
        base_pkgs: str = "lame atomicparsley faac "
        base_pkgs += "ffmpeg" if (not pkg_mgr.is_prog_present("ffmpeg") and not parser.is_present("-c")) else ""

        pkg_mgr.install_packages(
            apt=["sudo apt update", f"sudo apt -y install {base_pkgs}"],
            pacman=[f"sudo pacman --noconfirm -S {base_pkgs}"],
            dnf=["sudo dnf update", f"sudo dnf -y install {base_pkgs}"],
            zypper=["zypper update", f"zypper -n install {base_pkgs}"],
            emerge=[f"NON_INTERACTIVE=1 emerge {base_pkgs}"]
        )

    # Run the app
    if parser.is_present("-d"):

        # Create required directories if not present.
        if not path.isdir(STORAGE_FOLDER):
            makedirs(STORAGE_FOLDER)

        if not pkg_mgr.IS_WINDOWS:
            local_ip = check_output(("ip a | grep \"inet \" | grep -v \"127.0.0.1\" "  # noqa: S607
                                     "| awk -F ' ' {'print $2'} | cut -d \"/\" -f1"), shell=True)  # noqa: S602
            print(f" * My local ip address is: {local_ip.decode('utf-8').rstrip()}:{WSGI_PORT}")
            print(f" * My default interface is: {active_interface}")

        try:
            http_server = WSGIServer(('', WSGI_PORT), app, log=REQUEST_LOGLEVEL, error_log='default')
            http_server.serve_forever()
        except(KeyboardInterrupt):
            exit()


if __name__ == "__main__":
    main()
