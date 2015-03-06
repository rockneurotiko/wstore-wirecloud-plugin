# -*- coding: utf-8 -*-

# Copyright (c) 2012-2014 CoNWeT Lab., Universidad Politécnica de Madrid

# This file is part of Wirecloud.

# Wirecloud is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Wirecloud is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with Wirecloud.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import zipfile


class InvalidContents(Exception):
    pass


class WgtFile(object):

    _template_filename = 'config.xml'

    def __init__(self, _file):
        self._zip = zipfile.ZipFile(_file)

    def get_underlying_file(self):
        return self._zip.fp

    def read(self, path):
        return self._zip.read(path)

    def get_template(self):
        try:
            return self.read(self._template_filename)
        except KeyError:
            raise InvalidContents('Missing config.xml at the root of the zipfile (wgt)')

    def extract_file(self, file_name, output_path, recreate_=False):
        contents = self.read(file_name)

        dir_path = os.path.dirname(output_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        f = open(output_path, 'wb')
        f.write(contents)
        f.close()

    def extract_localized_files(self, file_name, output_dir):

        (file_root, ext) = os.path.splitext(file_name)
        search_re = re.compile(re.escape(file_root) + '(?:.\w\w(?:-\w\w)?)?' + re.escape(ext))
        for name in self._zip.namelist():
            if search_re.match(name):
                self.extract_file(name, os.path.join(output_dir, os.path.basename(name)))

    def extract_dir(self, dir_name, output_path):

        if not dir_name.endswith('/'):
            dir_name += '/'

        files = tuple(name for name in self._zip.namelist() if name.startswith(dir_name))

        if len(files) == 0:
            raise KeyError("There is no directory named '%s' in the archive" % dir_name)

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        for name in files:

            local_name = name[len(dir_name):]
            listnames = local_name.split("/")[:-1]
            folder = output_path
            if name.endswith("/"):
                for namedir in listnames:
                    folder += os.sep + namedir.replace("/", os.sep)
                    if (not os.path.exists(folder)
                        or (os.path.exists(folder) and not os.path.isdir(folder))):
                        os.mkdir(folder)
            else:
                for namedir in listnames:
                    folder += os.sep + namedir.replace("/", os.sep)
                    if not os.path.exists(folder) or not os.path.isdir(folder):
                        os.mkdir(folder)
                outfile = open(os.path.join(output_path, local_name.replace("/", os.sep)), 'wb')
                outfile.write(self._zip.read(name))
                outfile.close()

    def extract(self, path):

        if not os.path.exists(path) or not os.path.isdir(path):
            os.mkdir(path, 0o777)

        for name in self._zip.namelist():
            listnames = name.split("/")[:-1]
            folder = path
            if name.endswith("/"):
                for namedir in listnames:
                    folder += os.sep + namedir.replace("/", os.sep)
                    if (not os.path.exists(folder)
                        or (os.path.exists(folder) and not os.path.isdir(folder))):
                        os.mkdir(folder)
            else:
                for namedir in listnames:
                    folder += os.sep + namedir.replace("/", os.sep)
                    if not os.path.exists(folder) or not os.path.isdir(folder):
                        os.mkdir(folder)
                outfile = open(os.path.join(path, name.replace("/", os.sep)), 'wb')
                outfile.write(self._zip.read(name))
                outfile.close()

    def close(self):
        self._zip.close()